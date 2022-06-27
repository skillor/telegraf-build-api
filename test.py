from unittest import IsolatedAsyncioTestCase

from telegraf_builder.builder import BuildInfo
from telegraf_builder.plugins import Plugins


class Test(IsolatedAsyncioTestCase):
    async def test_build_os_arch(self):
        correct_builds = ["aix/ppc64", "android/386", "android/amd64", "android/arm", "android/arm64", "darwin/amd64",
                          "darwin/arm64", "dragonfly/amd64", "freebsd/386", "freebsd/amd64", "freebsd/arm",
                          "freebsd/arm64",
                          "illumos/amd64", "ios/amd64", "ios/arm64", "js/wasm", "linux/386", "linux/amd64", "linux/arm",
                          "linux/arm64", "linux/mips", "linux/mips64", "linux/mips64le", "linux/mipsle", "linux/ppc64",
                          "linux/ppc64le", "linux/riscv64", "linux/s390x", "netbsd/386", "netbsd/amd64", "netbsd/arm",
                          "netbsd/arm64", "openbsd/386", "openbsd/amd64", "openbsd/arm", "openbsd/arm64",
                          "openbsd/mips64",
                          "plan9/386", "plan9/amd64", "plan9/arm", "solaris/amd64", "windows/386", "windows/amd64",
                          "windows/arm", "windows/arm64"]
        for build in correct_builds:
            build_os, build_arch = build.split('/')
            info = BuildInfo(build_os, build_arch, Plugins({}))
            self.assertEqual(info.go_os, build_os)
            self.assertEqual(info.go_arch, build_arch)

        with self.assertRaises(Exception):
            BuildInfo('linus', 'amd64', Plugins({}))

        with self.assertRaises(Exception):
            BuildInfo('linux', 'snens42', Plugins({}))
