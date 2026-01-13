#custom error classes
class WeatherProviderError(Exception):
    pass

class WetaherNotFoundError(WeatherProviderError):
    pass