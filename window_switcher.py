from __future__ import annotations


import pywinctl as pwc
import time

from typing import Any, cast, List, Tuple, Union, TypedDict

def activeCB(active):
    print("NEW ACTIVE STATUS", active)

def movedCB(pos):
    print("NEW POS", pos)



# Global variables for window switcher


command_window_dict = {'loom': "rcu_tasks_rude_kthread",'bloom': "rcu_tasks_rude_kthread",'gloom': "rcu_tasks_rude_kthread",'blue': "rcu_tasks_rude_kthread",
                       'boom': "rcu_tasks_rude_kthread","share": "Obsidian", "ai": "Obsidian",
                       "drag drop":"Logseq" , "bullets":"Logseq" , "bullet":"Logseq" ,"editing":"Logseq" , "secure":"Logseq"}

def active_window_watcher():
    npw = pwc.getActiveWindow()
    npw.watchdog.start(isActiveCB=activeCB)
    npw.watchdog.setTryToFind(True)
    print("Toggle focus and move active window")
    print("Press Ctl-C to Quit")
    i = 0
    while True:
        try:
            if i == 50:
                npw.watchdog.updateCallbacks(isActiveCB=activeCB, movedCB=movedCB)
            if i == 100:
                npw.watchdog.updateInterval(0.1)
                npw.watchdog.setTryToFind(False)
            time.sleep(0.1)
        except KeyboardInterrupt:
            break
        i += 1
    npw.watchdog.stop()

class _WINDATA(TypedDict):
    id: Union[int, tuple[str, str]]
    display: list[str]
    position: tuple[int, int]
    size: tuple[int, int]
    status: int


class _WINDICT(TypedDict):
    pid: int
    windows: dict[str, _WINDATA]

def getAllWindowsDict(tryToFilter: bool = False) -> dict[str, _WINDICT]:
    """
    Get all visible apps and windows info

    Format:
        Key: app name

        Values:
            "pid": app PID
            "windows": subdictionary of all app windows
                "title": subdictionary of window info
                    "id": window handle
                    "display": display in which window is mostly visible
                    "position": window position (x, y) within display
                    "size": window size (width, height)
                    "status": 0 - normal, 1 - minimized, 2 - maximized

    :param tryToFilter: Windows ONLY. Set to ''True'' to try to get User (non-system) apps only (may skip real user apps)
    :return: python dictionary
    """
    result: dict[str, _WINDICT] = {}
    for win in pwc.getAllWindows():
        winId = win.getHandle()
        appName = win.getAppName()
        appPID = win._win.getPid()
        status = 0
        if win.isMinimized:
            status = 1
        elif win.isMaximized:
            status = 2
        pos = win.position
        size = win.size
        winDict: _WINDATA = {
            "id": winId,
            "display": win.getDisplay(),
            "position": (pos.x, pos.y),
            "size": (size.width, size.height),
            "status": status
        }
        if appName not in result.keys():
            result[appName] = {"pid": appPID, "windows": {}}
        result[appName]["windows"][win.title] = winDict
    return result

def get_all_windows():
    windows = pwc.getAllWindows()
    print(windows)

def get_all_window_app_names():
    # result: dict[str, List[str]] = {}
    result = {}
    for win in pwc.getAllWindows():
        appName = win.getAppName()
        if appName in result.keys():
            result[appName].append(win.getHandle())
        else:
            result[appName] = [win.getHandle()]
    return result

def get_active_titles():
    titles = pwc.getAllAppsNames()
    print(titles)



def lookup_command(command):
    global command_window_dict
    print(f"Received Command {command.lower()}")
    get_all_windows()
    print(get_all_window_app_names())
    # get_active_titles()
    try:
        command = command.strip(".")
        windowAppName = command_window_dict.get(f"{command.lower()}")
        print(windowAppName)
        for win in pwc.getAllWindows():
            appName = win.getAppName()
            if windowAppName == appName:
                win.activate()
            else:
                print("Window not in commands")
    except KeyError as error:
        print("Command not found")
