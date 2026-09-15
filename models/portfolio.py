

class portfolio:
    def __init__(self, name, assets):
        self.name = name
        self.assets = assets

    def total_value(self):
        return sum(asset.value for asset in self.assets)

    def add_asset(self, asset):
        self.assets.append(asset)

    def remove_asset(self, asset):
        self.assets.remove(asset)
