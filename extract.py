#!/usr/bin/env python3
import argparse
from pathlib import Path
from tqdm import tqdm
import requests
from bs4 import BeautifulSoup
from html_table_extractor.extractor import Extractor
import pandas as pd

def main(args):
	urls = {
		"tops": "https://animalcrossing.fandom.com/wiki/Clothing_(New_Horizons)/Tops",
		"bottoms": "https://animalcrossing.fandom.com/wiki/Clothing_(New_Horizons)/Bottoms",
		"dresses": "https://animalcrossing.fandom.com/wiki/Clothing_(New_Horizons)/Dresses",
		"hats": "https://animalcrossing.fandom.com/wiki/Clothing_(New_Horizons)/Hats",
		"accessories": "https://animalcrossing.fandom.com/wiki/Clothing_(New_Horizons)/Accessories",
		"socks": "https://animalcrossing.fandom.com/wiki/Clothing_(New_Horizons)/Socks",
		"shoes": "https://animalcrossing.fandom.com/wiki/Clothing_(New_Horizons)/Shoes",
		"bags": "https://animalcrossing.fandom.com/wiki/Clothing_(New_Horizons)/Bags",
		"umbrellas": "https://animalcrossing.fandom.com/wiki/Clothing_(New_Horizons)/Umbrellas",
	}
	for name, url in tqdm(urls.items()):
		page = requests.get(url).text

		soup = BeautifulSoup(page, "html.parser")
		extractor = Extractor(soup)
		extractor.parse()

		# Clean up
		df = pd.DataFrame(extractor.return_list())
		df = df.replace(r"\n", "", regex=True)

		# Strip all whitespace
		df_obj = df.select_dtypes(["object"])
		df[df_obj.columns] = df_obj.apply(lambda x: x.str.strip())

		# First row is the headers
		df.columns = df.iloc[0]
		df = df[1:]

		# Remove image column
		df = df.drop("Image", 1)

		with open(args.out_dir / f"{name}.md", "w") as file:
			file.write(df.to_markdown())


def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument("-o", "--out-dir", help="Place to store markdown output")

	args = parser.parse_args()
	if args.out_dir is not None:
		args.out_dir = Path(args.out_dir)

	return args


if __name__ == "__main__":
	main(parse_args())
