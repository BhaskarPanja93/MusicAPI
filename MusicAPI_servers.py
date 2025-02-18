from autoReRun import AutoReRun
while True:
    try:
        from Hidden.Secrets import RequiredFiles
        break
    except: input("Secrets.py not found in /Hidden")


toRun = {RequiredFiles.webServerRunnable: []}
toCheck = RequiredFiles.webServerRequired
interval = 1
AutoReRun(toRun, toCheck, interval)

