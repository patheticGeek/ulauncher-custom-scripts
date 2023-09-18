import subprocess
import os
import gi
gi.require_version("Gdk", "3.0")

from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.client.EventListener import EventListener

from src.functions import strip_list
from src.items import no_config_items, no_results_item, generate_launcher_items
from src.scripts import Scripts


class CustomSearchExtension(Extension):
    def __init__(self):
        super(CustomSearchExtension, self).__init__()

        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, RunCommand())


class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        query = event.get_argument() or str()
        launcher = Scripts(strip_list(query.split(' ')))

        if not launcher.has_config():
            return RenderResultListAction(no_config_items())

        if launcher.has_query():
            results, params = launcher.execute()
        else:
            results, params = launcher.get_first_scripts()

        if not results or len(results) == 0:
            return RenderResultListAction(no_results_item())

        return RenderResultListAction(generate_launcher_items(results, params))

class RunCommand(EventListener):

    def on_event(self, event, extension):

        data = event.get_data()

        terminal = extension.preferences["term"]
        exec = extension.preferences["exec"]
        command = data
        shell = extension.preferences["shell"]

        envUserShell = os.environ["SHELL"] if data["exit_after"] != "true" else ""

        if shell == "fish":
            subprocess.run( [f'{terminal} {exec} {envUserShell} -c "{command}; {envUserShell}"'], shell=True )
        else:
            subprocess.run( [f'{terminal} {exec} {envUserShell} -c -i "{command}; {envUserShell}"'], shell=True )

        return HideWindowAction()


if __name__ == "__main__":
    CustomSearchExtension().run()
