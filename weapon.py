class Weapon(list):

    def __init__(self,weaponName,description,weaponClass,imageURL):
        self.weaponName = weaponName
        self.description = description
        self.weaponClass = weaponClass
        self.imageURL = imageURL

    def getStats(self):
        return self.Stats.__repr__(self)

    def stats(self,hitDamage, range, singleFireAcc, autoFireAcc, recoilControl, fireRate, magCapacity, mobility):
        self.Stats.__init__(self,hitDamage, range, singleFireAcc, autoFireAcc, recoilControl, fireRate, magCapacity, mobility)

    def mod(self,modName,modStat,valueModifier):
        self.Mod.__init__(self,modName,modStat,valueModifier)

    def getMod(self):
        return self.Mod.__repr__(self)

    def __repr__(self):
        return "Weapon('{}', '{}', '{}', '{}')".format(self.weaponName,self.description,self.weaponClass,self.imageURL)

#------------------------------------------------------------------------------------------------------------------

    class Mod(list):

        def __init__(self,modName,modStat,valueModifier):
            self.modName = modName
            self.modStat = modStat
            self.valueModifier = valueModifier

        def __repr__(self):
            return "Mod('{}', '{}', '{}')".format(self.modName,self.modStat,self.valueModifier)

#------------------------------------------------------------------------------------------------------------------

    class Stats:

        def __init__(self,hitDamage, range, singleFireAcc, autoFireAcc, recoilControl, fireRate, magCapacity, mobility):
            self.hitDamage = hitDamage
            self.range = range
            self.singleFireAcc = singleFireAcc
            self.autoFireAcc = autoFireAcc
            self.recoilControl = recoilControl
            self.fireRate = fireRate
            self.magCapacity = magCapacity
            self.mobility = mobility


        def __repr__(self):
            return "Stats('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(self.hitDamage,self.range,self.singleFireAcc,self.autoFireAcc,self.recoilControl,self.fireRate,self.magCapacity,self.mobility)
