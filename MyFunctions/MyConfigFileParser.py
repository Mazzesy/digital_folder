import configparser


class MyConfigFileParser:

    @staticmethod
    def write_config_file(key, item, section, config_path):
        config = configparser.ConfigParser()
        config.read(config_path)
        config[section][key] = item

        with open(config_path, 'w') as configfile:  # save
            config.write(configfile)

    @staticmethod
    def load_config_file(key, section, config_path):
        config = configparser.ConfigParser()
        config.read(config_path)

        return config[section][key]
