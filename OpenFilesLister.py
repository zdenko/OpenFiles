import sublime_plugin
import sublime
import os

def win_name(wnd, name):
    pname = wnd.project_file_name()
    if pname:
        return str(pname).split("/")[-1].split(".sublime-project")[0]

    if name == None:
        return ""

    nfolders = len(wnd.folders())
    # print(fname)
    name1 = name.rsplit(os.sep, -1)
    if len(name1) > 3:
        fname = "../" + name1[-2]
    else:
        fname = name1[-1]
    if fname:
        return fname

    return ""



# Created: 18-04-2018
class OpenFilesListerCommand(sublime_plugin.WindowCommand):
    def run(self, glob_views = False):
        self.window = sublime.active_window()

        self.windows = {}
        self.sheets = []
        self.filePaths = []
        self.fileNames = []
        self.viewIds = []
        self.viewIdW = {}

        self.untitled = self.get_setting("show_untitled_files")

        count = 0

        wins = sublime.windows() if glob_views else [self.window]
        for wnd in wins:
            for sheet in wnd.sheets():
                if not(sheet and sheet.view()):
                    continue

                name = sheet.view().file_name()
                self.windows[wnd.id()] = {"id": wnd.id(), "wnd": wnd, "title": win_name(wnd, name) }
                self.viewIdW[sheet.view().id()] = wnd.id()
                if name != None:
                    self.sheets.append(sheet.view())
                    vId = sheet.view().id()
                    vvId = self.viewIdW[vId]
                    name = os.path.abspath(sheet.view().file_name())
                    fname = self.windows[vvId]["title"]
                    name1 = name.rsplit(os.sep, -1)[-1]
                    if fname != "":
                        name1 = name1 + " (" + fname + ")"
                    self.fileNames.append(name1)
                    self.filePaths.append(name)
                    self.viewIds.append(vId)
                elif name == None and self.untitled == True:
                    temp = sheet.view().name()
                    self.sheets.append(sheet.view())
                    self.fileNames.append("Untitled-{}* {}".format(count, temp))
                    self.filePaths.append("Untitled-{}{}".format(count, temp))
                    self.viewIds.append(sheet.view().id())
                    count = count + 1

        id = self.window.active_sheet().view().id()

        if id not in self.viewIds:
            self.window.run_command("next_view_in_stack")
            id = self.window.active_sheet().view().id()

        self.current = self.viewIds.index(id)
        # print (self.viewIds)
        self.window.run_command("hide_overlay")

        self.show_panel()

    def is_this_window(self, index):
        v = self.sheets[index]
        widx = self.viewIdW[v.id()]
        return widx == self.window.id()

    def show_panel(self):
        self.window.show_quick_panel(self.fileNames, self.on_done, selected_index=self.current, on_highlight=self.on_highlighted)

    def set_timeout(self):
        sublime.set_timeout_async(lambda: self.close_panel(), 1500)

    def close_panel(self):
        self.window.run_command("hide_overlay")

    def on_done(self, index):
        if index == -1:
            index = self.current
        # get window
        v = self.sheets[index]
        widx = self.viewIdW[v.id()]
        w = self.windows[widx]
        # print( widx, index, self.sheets)
        w["wnd"].bring_to_front()
        w["wnd"].focus_view(v)

    def on_highlighted(self, index):
        return
        # if self.is_this_window(index):
        #     self.window.focus_view(self.sheets[index])

    def get_settings(self):
        return sublime.load_settings('OpenFilesLister.sublime-settings')

    def get_setting(self, setting):
        return self.get_settings().get(setting)
