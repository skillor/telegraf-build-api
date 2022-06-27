import asyncio
import os
import shutil
import threading
from concurrent import futures
from typing import *
import uuid
import subprocess

from .cleaner import rm_dir
from .installer import get_git_info
from .plugins import Plugins

if TYPE_CHECKING:
    from .plugin_manager import PluginManager


AVAILABLE_GO_OS = {
    'aix': ['ppc64'],
    'android': ['386', 'amd64', 'arm', 'arm64'],
    'darwin': ['amd64', 'arm64'],
    'dragonfly': ['amd64'],
    'freebsd': ['386', 'amd64', 'arm', 'arm64'],
    'illumos': ['amd64'],
    'ios': ['amd64', 'arm64'],
    'js': ['wasm'],
    'linux': ['386', 'amd64', 'arm', 'arm64', 'mips', 'mips64', 'mips64le',
              'mipsle', 'ppc64', 'ppc64le', 'riscv64', 's390x'],
    'netbsd': ['386', 'amd64', 'arm', 'arm64'],
    'openbsd': ['386', 'amd64', 'arm', 'arm64', 'mips64'],
    'plan9': ['386', 'amd64', 'arm'],
    'solaris': ['amd64'],
    'windows': ['386', 'amd64', 'arm', 'arm64'],
}


class BuildInfo:
    def __init__(self, go_os: str, go_arch: str, plugins: Plugins):
        if go_os not in AVAILABLE_GO_OS:
            raise Exception('GO OS "{}" unknown'.format(go_os))
        if go_arch not in AVAILABLE_GO_OS[go_os]:
            raise Exception('GO ARCH "{}" unknown'.format(go_arch))
        self.go_os = go_os
        self.go_arch = go_arch
        self.plugins = plugins
        self.cached = False
        self.uuid = None
        self.built_binary_path = None
        self.original_name = None

    def __hash__(self):
        return hash((self.go_os, self.go_arch, self.plugins))


class AsyncEvent(asyncio.Event):
    def set(self):
        # TODO: _loop is not documented
        self._loop.call_soon_threadsafe(super().set)


class BinaryBuilder:
    def __init__(self, builder: 'Builder', build_info: BuildInfo, event: asyncio.Event):
        self.result = None
        self.error = None
        self.builder = builder
        self.build_info = build_info
        self.finished = False
        self.event = event

    def build(self):
        try:
            self.builder.build(self.build_info)
        except Exception as err:
            self.error = err
        self.finished = True
        self.event.set()


class Builder:
    def __init__(self, plugin_manager: 'PluginManager', telegraf_dir: str, build_dir: str, binary_dir: str):
        self.plugin_manager = plugin_manager
        self.telegraf_dir = telegraf_dir
        self.source_info = get_git_info(telegraf_dir)
        if not os.path.exists(build_dir):
            os.makedirs(build_dir)
        self.build_dir = build_dir
        if not os.path.exists(binary_dir):
            os.makedirs(binary_dir)
        self.binary_dir = binary_dir

        self.thread_pool = futures.ThreadPoolExecutor()
        self.cached_binaries: Dict[int, 'BinaryBuilder'] = {}

    async def get_binary_by_build_id(self, build_id: str) -> BuildInfo:
        for binary_builder in self.cached_binaries.values():
            if binary_builder.build_info.uuid == build_id:
                binary_builder.build_info.cached = True
                await binary_builder.event.wait()
                if binary_builder.error is not None:
                    raise binary_builder.error
                return binary_builder.build_info
        raise Exception('Binary with build id "{}" not found'.format(build_id))

    async def get_binary(self, go_os: str, go_arch: str, plugins: Plugins) -> BuildInfo:
        build_info = BuildInfo(go_os, go_arch, plugins)
        build_info_hash = build_info.__hash__()
        if build_info_hash in self.cached_binaries:
            cached_build = self.cached_binaries[build_info_hash]
            cached_build.build_info.cached = True
            await cached_build.event.wait()
            if cached_build.error is not None:
                raise cached_build.error
            return cached_build.build_info

        bb = BinaryBuilder(self, BuildInfo(go_os, go_arch, plugins), AsyncEvent())
        self.cached_binaries[build_info_hash] = bb
        threading.Thread(target=bb.build).start()
        await bb.event.wait()
        if bb.error is not None:
            raise bb.error
        return bb.build_info

    def build(self, build_info: BuildInfo):
        build_id = uuid.uuid4().hex
        working_dir = os.path.join(self.build_dir, build_id)
        shutil.copytree(self.telegraf_dir, working_dir)

        self.plugin_manager.set_plugins(working_dir, build_info.plugins)

        build_path = os.path.join(working_dir, 'build' + os.sep)

        result = subprocess.run(['go', 'build', '-o', build_path, './cmd/telegraf'],
                                shell=False,
                                cwd=working_dir,
                                env=dict(os.environ, GOOS=build_info.go_os, GOARCH=build_info.go_arch),
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL,
                                )
        if result.returncode != 0:
            raise Exception('Go build failed')

        build_files = os.listdir(build_path)
        if len(build_files) != 1:
            raise Exception('Go build produced more than 1 file')

        build_file = build_files[0]
        build_info.original_name = build_file

        build_info.uuid = build_id
        build_info.built_binary_path = os.path.join(self.binary_dir, build_id)
        os.rename(os.path.join(build_path, build_file), build_info.built_binary_path)

        rm_dir(working_dir)
