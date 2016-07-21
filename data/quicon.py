import hera_config

h350=hera_config.HeraConfig(350)
h243=hera_config.HeraConfig(243)
h37 =hera_config.HeraConfig(37)

h350.plot(onlyAnts=True,fignum='h350/243')
h243.plot(coreColor='m',onlyAnts=True)

h243.subtract(h37,'plotit')
