from enum import Enum

class LightningMode(Enum):
    Disabled = 'disabled'
    Error = 'error'
    Loading = 'loading'
    Running = 'running'

refresh = {
    LightningMode.Disabled : 0.25,
    LightningMode.Error : 0.5,
    LightningMode.Loading : 0.05,
    LightningMode.Running  : 1
}

NB_LOADING_LED = 10
