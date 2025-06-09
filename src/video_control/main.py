import sys
import asyncio
from pathlib import Path
from PyQt5.QtWidgets import QApplication

THIS_FILE = Path(__file__).resolve()
SRC_ROOT = THIS_FILE.parents[1]    
sys.path.append(str(SRC_ROOT))

from .ui.mainTab import MainWindow
from .app_ini import Inicializator

def main():
    ini = Inicializator()
    auth_svc, cam_svc, shelf_svc, stream_svc, config_editor = \
        asyncio.run(ini.initialize())

    app = QApplication(sys.argv)
    w = MainWindow(
        auth_service=auth_svc,
        camera_service=cam_svc,
        shelving_service=shelf_svc,
        stream_service=stream_svc,
        config_editor=config_editor
    )
    w.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()