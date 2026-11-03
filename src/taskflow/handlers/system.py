import platform
import os
from datetime import datetime, timezone

from .base import BaseHandler


class SystemReportHandler(BaseHandler):

    def execute(self, **kwargs):

        report = {
            "platform": platform.system(),
            "platform_release": platform.release(),
            "architecture": platform.machine(),
            "processor": platform.processor() or "Unknown",
            "cpu_count": os.cpu_count(),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        return report