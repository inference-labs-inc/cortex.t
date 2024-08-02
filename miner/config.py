from dotenv import load_dotenv
import argparse
import os
from pathlib import Path

import bittensor as bt


class Config(bt.config):
    def __init__(self):
        super().__init__()
        load_dotenv()  # Load environment variables from .env file

        self.ENV = os.getenv('ENV')

        self.WANDB_API_KEY = os.getenv('WANDB_API_KEY')
        self.OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
        self.GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
        self.ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
        self.GROQ_API_KEY = os.getenv('GROQ_API_KEY')
        self.AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
        self.AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')
        self.PIXABAY_API_KEY = os.getenv('PIXABAY_API_KEY')

        self.CORTEXT_MINER_ADDITIONAL_WHITELIST_VALIDATOR_KEYS = os.getenv(
            'CORTEXT_MINER_ADDITIONAL_WHITELIST_VALIDATOR_KEYS')
        self.RICH_TRACEBACK = os.getenv('RICH_TRACEBACK')

        self.WALLET_NAME = os.getenv('WALLET_NAME')
        self.HOT_KEY = os.getenv('HOT_KEY')
        self.NET_UID = os.getenv('NET_UID')
        self.ASYNC_TIME_OUT = os.getenv('ASYNC_TIME_OUT')
        self.AXON_PORT = os.getenv('AXON_PORT', 8098)
        self.EXTERNAL_IP = os.getenv('EXTERNAL_IP')

        self.BT_SUBTENSOR_NETWORK = 'finney' if self.ENV == 'prod' else 'test'
        self.WANDB_OFF = False if self.ENV == 'prod' else True
        self.LOGGING_TRACE = False if self.ENV == 'prod' else True
        self.BLOCKS_PER_EPOCH = os.getenv('BLOCKS_PER_EPOCH', 100)
        self.WAIT_NEXT_BLOCK_TIME = os.getenv('WAIT_NEXT_BLOCK_TIME', 1)
        self.NO_SET_WEIGHTS = os.getenv('NO_SET_WEIGHTS', False)
        self.NO_SERVE = os.getenv('NO_SERVE', False)

    def __repr__(self):
        return (
            f"Config(BT_SUBTENSOR_NETWORK={self.BT_SUBTENSOR_NETWORK}, WALLET_NAME={self.WALLET_NAME}, HOT_KEY={self.HOT_KEY}"
            f", NET_UID={self.NET_UID}, WANDB_OFF={self.WANDB_OFF}, LOGGING_TRACE={self.LOGGING_TRACE}")


config = Config()


def check_config(cls, config: bt.config):
    bt.axon.check_config(config)
    bt.logging.check_config(config)
    full_path = Path(f'{config.logging.logging_dir}/{config.wallet.get("name", bt.defaults.wallet.name)}/'
                     f'{config.wallet.get("hotkey", bt.defaults.wallet.hotkey)}/{config.miner.name}').expanduser()
    config.miner.full_path = str(full_path)
    full_path.mkdir(parents=True, exist_ok=True)


def get_config() -> bt.config:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--axon.port", type=int, default=8098, help="Port to run the axon on."
    )
    # External IP 
    parser.add_argument(
        "--axon.external_ip", type=str, default=bt.utils.networking.get_external_ip(), help="IP for the metagraph"
    )
    # Subtensor network to connect to
    parser.add_argument(
        "--subtensor.network",
        default="finney",
        help="Bittensor network to connect to.",
    )
    # Chain endpoint to connect to
    parser.add_argument(
        "--subtensor.chain_endpoint",
        default="wss://entrypoint-finney.opentensor.ai:443",
        help="Chain endpoint to connect to.",
    )
    # Adds override arguments for network and netuid.
    parser.add_argument("--netuid", type=int, default=1, help="The chain subnet uid.")

    parser.add_argument(
        "--miner.root",
        type=str,
        help="Trials for this miner go in miner.root / (wallet_cold - wallet_hot) / miner.name ",
        default="~/.bittensor/miners/",
    )
    parser.add_argument(
        "--miner.name",
        type=str,
        help="Trials for this miner go in miner.root / (wallet_cold - wallet_hot) / miner.name ",
        default="Bittensor Miner",
    )

    # Run config.
    parser.add_argument(
        "--miner.blocks_per_epoch",
        type=str,
        help="Blocks until the miner sets weights on chain",
        default=100,
    )

    # Switches.
    parser.add_argument(
        "--miner.no_set_weights",
        action="store_true",
        help="If True, the miner does not set weights.",
        default=False,
    )
    parser.add_argument(
        "--miner.no_serve",
        action="store_true",
        help="If True, the miner doesnt serve the axon.",
        default=False,
    )
    parser.add_argument(
        "--miner.no_start_axon",
        action="store_true",
        help="If True, the miner doesnt start the axon.",
        default=False,
    )

    # Mocks.
    parser.add_argument(
        "--miner.mock_subtensor",
        action="store_true",
        help="If True, the miner will allow non-registered hotkeys to mine.",
        default=False,
    )

    parser.add_argument('--test', action='store_true', help='Use test configuration')

    # Adds subtensor specific arguments i.e. --subtensor.chain_endpoint ... --subtensor.network ...
    bt.subtensor.add_args(parser)

    # Adds logging specific arguments i.e. --logging.debug ..., --logging.trace .. or --logging.logging_dir ...
    bt.logging.add_args(parser)

    # Adds wallet specific arguments i.e. --wallet.name ..., --wallet.hotkey ./. or --wallet.path ...
    bt.wallet.add_args(parser)

    # Adds axon specific arguments i.e. --axon.port ...
    bt.axon.add_args(parser)

    # Activating the parser to read any command-line inputs.
    # To print help message, run python3 template/miner.py --help
    config = bt.config(parser)

    # Logging captures events for diagnosis or understanding miner's behavior.
    full_path = Path(f"{config.logging.logging_dir}/{config.wallet.name}/{config.wallet.hotkey}"
                     f"/netuid{config.netuid}/miner").expanduser()
    config.full_path = str(full_path)
    # Ensure the directory for logging exists, else create one.
    full_path.mkdir(parents=True, exist_ok=True)
    return config
