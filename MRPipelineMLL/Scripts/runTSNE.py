import sys
import os
sys.path.insert(0, os.getcwd() + "\\MRPipelineMLL") # location of src 
from Statistics.tsne import CustomTSNE
import Utility.utility as util
import numpy as np
import Utility.config as config

customTSNE = CustomTSNE("Data\\DataAnalysis\\featureDatabasesStandardized.npz", "Data\\DataAnalysis\\distributionDatabasesNorm.npz")
#customTSNE = CustomTSNE("Data\\DataAnalysis\\featureDatabases.npz", "Data\\DataAnalysis\\distributionDatabasesNorm.npz")

config.initialize(skip_renderer=True)
config.lg.set_to_write()


# include_list_good = ["Bicycle", "Knife", "Bookset", "Sword", "Helicopter", "Quadruped", "Wheelchair", 'Biplane']
#customTSNE.show_tsne(include=include_list)
#customTSNE.test_tsne_values(max_iter=(250,500,50), perplexity=(5,20,5))
#customTSNE.test_tsne_values(test_case_folder_name="long_list_good_exag", include=include_list_good, max_iter=(500,3000,250), perplexity=(10,50,5), early_exaggeration=(4,20,2))

include_list_bad = ["BuildingNonResidential", "Skyscraper", "House", "Apartment", "Sign", "Drum", "Bus", 'Vase']
# customTSNE.test_tsne_values(test_case_folder_name="long_list_bad_exag", include=include_list_bad, max_iter=(500,3000,250), perplexity=(10,50,5), early_exaggeration=(4,20,2))
customTSNE.show_tsne(include=include_list_bad)

# All Classes
'''AircraftBuoyant' 'Apartment' 'AquaticAnimal' 'Bed' 'Bicycle' 'Biplane'
 'Bird' 'Bookset' 'Bottle' 'BuildingNonResidential' 'Bus' 'Car'
 'Cellphone' 'Chess' 'City' 'ClassicPiano' 'Computer' 'ComputerKeyboard'
 'Cup' 'DeskLamp' 'DeskPhone' 'Door' 'Drum' 'Fish' 'FloorLamp' 'Glasses'
 'Guitar' 'Gun' 'Hand' 'Hat' 'Helicopter' 'House' 'HumanHead' 'Humanoid'
 'Insect' 'Jet' 'Knife' 'MilitaryVehicle' 'Monitor' 'Monoplane'
 'Motorcycle' 'Mug' 'MultiSeat' 'Musical_Instrument' 'NonWheelChair'
 'PianoBoard' 'PlantIndoors' 'PlantWildNonTree' 'Quadruped'
 'RectangleTable' 'Rocket' 'RoundTable' 'Shelf' 'Ship' 'Sign' 'Skyscraper'
 'Spoon' 'Starship' 'SubmachineGun' 'Sword' 'Tool' 'Train' 'Tree' 'Truck'
 'TruckNonContainer' 'Vase' 'Violin' 'Wheel' 'WheelChair'''

#Good
'''Bycicle Fish Bookset Sword Helicopter (Jet) Quadruped Wheelchair Biplane'''

#Bad
'''BuildingNonResidential Skyscraper House Apartment Sign Drum Bus Vase'''