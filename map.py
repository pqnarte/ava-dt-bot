class Map(list):

    def __init__(self,mapName,maplayoutURL,mapvideo):
        self.mapName = mapName
        self.maplayoutURL = maplayoutURL
        self.mapvideo = mapvideo

    def __repr__(self):
        return "Weapon('{}', '{}', '{}', '{}')".format(self.weaponName,self.description,self.weaponClass,self.imageURL)
