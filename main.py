#El modelo es pesado, asi que es posible que si el computador es lento o tiene poca ram, el codigo saque error cuando se intenta cargar
import gui
import reportLog
if __name__ == "__main__":
    logReport = reportLog.ReportLog()
    logReport.logger.info("Init main")
    gui.main() 