import subprocess
import config
import multiprocessing as mp
NUM_BOTS = 2
assert NUM_BOTS <= len(config.BOT_TOKENS_), 'fewer tokens than bots!'

# possible bugfix for windows multiprocessing
# https://stackoverflow.com/questions/8804830/python-multiprocessing-picklingerror-cant-pickle-type-function


def main():
    print('WARNING: run_more_bots is deprecated')
    pool = mp.Pool()

    processes_ = []
    for bot_idx in range(NUM_BOTS):
        bot_process = BotProcess(bot_idx)
        processes_.append(bot_process)

    pool.map(run, processes_)
    pool.close()
    pool.join()


def run(bot_process):
    bot_process.run()


class BotProcess():
    def __init__(self, bot_idx):
        self.bot_idx = bot_idx

    def run(self):
        print('Starting process: ' + str(self.bot_idx))
        subprocess.call([
            'python', 'main.py',
            '--bot_idx', str(self.bot_idx)
        ])


if __name__ == "__main__":
    main()
