
class SentimentAnalysisConfig:
    """ SentimentAnalysisConfig class.... """

    _instance: SentimentAnalysisConfig | None = None
    _settings: Dict[str, Any] = {}
    _initialized: bool = False

    log = LoggingMixin().log

    def __new__(cls, *args: Any, **kwargs: Any) \
            -> SentimentAnalysisConfig:
        """ Creates and initializes a singleton instance of this class.... """

        if cls._instance is None:
            cls._instance = super(SentimentAnalysisConfig, cls).__new__(cls)

        cls._initialize(*args, **kwargs)
        return cls._instance

    @classmethod
    def _initialize(
            cls,
            api: str = '',
            llm: T | None = None,
            from_sample: int = 0,
            to_sample: int = 9999999,
            batch_size: int = 100,
            data_offset: int = 0,
            n_batches: int = 1,
            chunk_size: int = 15,
            prompt_group: List[int] = None,
            version: str = '00',
            balance: int = 33,
            balanced: bool = False,
            n_best_prompts: int = 5,
            target_n_prompts: int = 150,
            with_validation: bool = True,
    ) -> None:
        """ Initializes the configuration settings with the provided values. """

        if not cls._initialized:
            cls.set('api', api)
            cls.set('llm', llm)
            cls.set('from_sample', from_sample)
            cls.set('to_sample', to_sample)
            cls.set('batch_size', batch_size)
            cls.set('data_offset', data_offset)
            cls.set('n_batches', n_batches)
            cls.set('chunk_size', chunk_size)
            cls.set('prompt_group', prompt_group)
            cls.set('version', version)
            cls.set('balance', balance)
            cls.set('balanced', balanced)
            cls.set('n_best_prompts', n_best_prompts)
            cls.set('target_n_prompts', target_n_prompts)
            cls.set('with_validation', with_validation)

            cls._initialized = True

    @classmethod
    def get(cls, key: str) \
            -> Any:
        """
        Retrieves the value associated with a given key from the settings....
        """

        return cls._settings.get(key)

    @classmethod
    def set(cls, key: str, val: Any) \
            -> None:
        """ Sets the value for a given key in the settings.....  """

        cls._settings[key] = val

    @classmethod
    def validate(cls) \
            -> None:
        """ Validates config settings for logical consistency...."""

        batch_size = cls.get('batch_size')
        balance = cls.get('balance')
        balanced = cls.get('balanced')

        if balanced and batch_size % (3 * balance) != 0:
            raise CriticalException(
                Logger(
                    f"{inspect.currentframe().f_code.co_name}"
                ).get_logger(),
                (
                    "Batch size must be a multiple of 3 times the balance "
                    "value when balanced=True."
                )
            )

    @classmethod
    def remove(cls, key: str) \
            -> None:
        """
        Removes a key-value pair from the settings.

        Parameters
        ----------
        key : str
            The key to remove from the settings.

        """

        if key in cls._settings:
            del cls._settings[key]

    @classmethod
    def update(cls, **kwargs) \
            -> None:
        """
        Updates multiple settings at once based on provided keyword arguments.

        Parameters
        ----------
        kwargs : Any
            Key-value pairs of settings to update.

        Examples
        --------
        >>> config = SentimentAnalysisConfig()
        >>> config.update(version='01', balanced=True)

        """

        for key, value in kwargs.items():
            cls.set(key, value)

    @classmethod
    def reset_instance(cls) \
            -> None:
        """
        Resets the single instance of this class.

        This method is needed to reinitialize the class for test purposes.

        """

        cls._instance = None
        cls._initialized = False

    @classmethod
    def print(cls) \
            -> None:
        """
        Prints the current settings.
        """

        title = "Settings in SentimentAnalysisConfig"
        body = cls.to_str()
        print_in_box(title, body)

    @classmethod
    def to_str(cls) \
            -> str:
        """
        Returns a string representation of the settings.

        Returns
        -------
        str
            The string representation of the settings.

        """

        string = ''
        for key, val in cls._settings.items():
            string = f"{string}{key}:\t{val}\n"

        return string
