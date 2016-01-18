import configparser

Config = configparser.ConfigParser()
Config.read("names.cfg")


def LoadSyllables(section):
    dict1 = {}
    options = Config.options(section)
    for option in options:
        try:
            if dict1[option] == -1:
                print("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1
