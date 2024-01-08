import rpi_sentry_core.api as api


class RealCamera(api.Camera):
    def shoot(self, rank):
        print("real camera shoot")
