import re
from typing import Any
from typing import Dict, List
import requests
from bs4 import BeautifulSoup, ResultSet
from fastapi import HTTPException, Request
from starlette.datastructures import QueryParams
from configurations.properties import OK_STATUS, GAME_WIKI_URL, EXTERNAL_LINK_PREFIX
from models.attribute_value import AttributeValue


class GameParser():
    RATING_ATTRIBUTE_NAME = "Rating(s)"
    RELEASE_ATTRIBUTE_NAME = "Release date(s)"

    def __init__(self):
        self.game_response: Dict= {}
        self.last_key: str = ""

    def create_parser(self, game_name: str) -> BeautifulSoup:
        """
        Creates web parser object

        :param game_name: Name of the target game
        :return: BeautifulSoup parser
        """
        game_info = self.get_game_info(game_name)
        return BeautifulSoup(game_info, "html.parser")

    def parse_game_info(self, game_name: str) -> Dict:
        """
        Will parse for generic game information
        Includes table of content and info box

        :param game_name: Name of the target game
        :return: Generic Game Info Dictionary Response
        """
        parser: BeautifulSoup = self.create_parser(game_name)
        self.parse_table_info(parser)
        self.build_table_of_content_response(self.parse_table_of_content(parser))
        return self.game_response

    def get_game_info(self, game_name: str) -> str:
        """
        Will make the request to retrieve the raw game content from the wiki page

        :param game_name: Name of the Game
        :return: Raw Page Text
        """
        target_url = f"{GAME_WIKI_URL}{game_name}"

        response = requests.get(target_url)

        if response.status_code != OK_STATUS:
            raise HTTPException(status_code=response.status_code, detail=response.reason)
        return response.text

    def parse_table_info(self, parser: BeautifulSoup) -> None:
        """
        Will parse the content of the info table

        :param parser: BeautifulSoup Parser
        """
        table: ResultSet = parser.find_all(name="table", attrs={'class': 'infobox'})

        for info in table:
            for current in info.find_all(name="tr"):
                attribute_key = current.find(name="th")
                if attribute_key:
                    attribute_key = attribute_key.get_text()

                value = current.find_all(name="a")
                if value:
                    value = [AttributeValue(content=temp.get_text(), link=temp.get('href')) for temp in value if temp]
                elif current.find(name="td"):
                    value = [AttributeValue(content=current.find(name="td").get_text(), link=None)]
                else:
                    value = None

                # Rating value edge condition
                if attribute_key == GameParser.RATING_ATTRIBUTE_NAME and current.find(name="div",
                                                                                      attrs={'class': 'rating'}):
                    value = [AttributeValue(
                        content=current.find(name="div", attrs={'class': 'rating'}).get_text().replace(" ", ""),
                        link=None)]
                self.build_table_response(attribute_key, value)

    def build_table_response(self, attribute_key: str, value: List[AttributeValue]) -> None:
        """
        Will build the game response based on the key and value pairs extracted

        :param attribute_key: Info Table Attribute Key
        :param value: Info Table Possible Attribute Values
        """
        if attribute_key is not None:
            if self.last_key is not None and self.last_key:
                if self.last_key in self.game_response.keys() and self.game_response[self.last_key] is None:
                    self.game_response.pop(self.last_key)
            self.last_key = attribute_key
            self.game_response[attribute_key] = self.parse_value(attribute_key, value)
        elif attribute_key is None and self.game_response[self.last_key] is None:
            if value[0].content == '':
                self.game_response.pop(self.last_key)
            else:
                self.game_response[self.last_key] = self.parse_value(attribute_key, value)

    def parse_value(self, attribute_key: str, value: List[AttributeValue]) -> Any:
        """
        Will determine how to build the game response key and value pair for info table.
        Pair Combinations Include:
        1. string: string
        2. string: list[string]
        3. string: dictionary{string, string}
        4. string: None

        :param attribute_key: Info Table Attribute Key
        :param value: Info Table Possible Attribute Values
        :return: Will return one of the 4 possible pairs
        """
        if value:
            if len(value) == 1 and (value[0].link is None or not value[0].link.startswith(EXTERNAL_LINK_PREFIX)):
                return value[0].content

            list_content: bool = all(
                [True if not temp.link.startswith(EXTERNAL_LINK_PREFIX) else False for temp in value])

            if list_content:
                temp_list: List[str] = []
                month_date = year = system = country = ""
                for current in value:
                    # Year key edge condition
                    if attribute_key == GameParser.RELEASE_ATTRIBUTE_NAME:
                        if current.content:
                            try:
                                year = int(current.content)
                                release_date = "{}{}{}: {}, {}".format(country, ', ' if system else '', system,
                                                                       month_date,
                                                                       year)
                                temp_list.append(release_date)
                            except:
                                month_date = current.content
                        elif current.link.endswith('_icon.png'):
                            link = current.link
                            system = link[link.find(':') + 1:].replace('_icon.png', '').replace('_', ' ')
                        elif current.link.endswith('.svg'):
                            link = current.link
                            country = re.sub('Flag of (the )?', '',
                                             link[link.find(':') + 1:].replace('.svg', '').replace('_', ' '))
                    else:
                        if current.content:
                            temp_list.append(current.content)
                return temp_list
            else:
                temp_dict: Dict = {}
                for current in value:
                    temp_dict[current.content] = current.link
                return temp_dict
        return None

    def parse_table_of_content(self, parser: BeautifulSoup) -> Dict:
        """
        Will parse the table of content section for the target game.

        :param parser: BeautifulSoup Parser
        :return: Table of Content Dictionary Data
        """
        content_table = parser.find(name="ul", attrs={'class': 'level-1'})
        current = content_table.find(name="span")
        deprecated_page = "redlink=1"
        table_of_content_data: Dict[str, List[Dict[str, str]]] = {}
        parent = child = ""

        while current:
            if current.find_next_sibling(name="ul", attrs={'class': ['level-2', 'level-3', 'level-4', 'level-5']}):
                parent = current.get_text()
            elif current.find(name='a'):
                link = current.find(name='a').get('href')
                attribute = current.find(name='a').get_text().title()

                if deprecated_page not in link:
                    child = {attribute: link}
                    if table_of_content_data.get(parent) is not None:
                        table_of_content_data[parent].append(child)
                    else:
                        table_of_content_data[parent] = [child]
                elif table_of_content_data.get(parent) is None:
                    table_of_content_data[parent] = []
            else:
                table_of_content_data[current.get_text()] = []

            current = current.find_next(name='span')

        return table_of_content_data

    def build_table_of_content_response(self, table_of_content_data: Dict[str, List[Dict[str, str]]]) -> None:
        """
        Takes in a table of content data dictionary which will extract information for the game response JSON

        :param table_of_content_data: Table of Content data dictionary
        """
        api_options: Dict[str, List[str]] = {}
        for key, value in table_of_content_data.items():
            api_options[key] = [next(iter(current.keys())) for current in value]

        self.game_response["API-Options"] = api_options

    def get_content_info(self, game_name: str, request: Request):
        """
        Get API-Options content info
        Note: For now it provides link to the respective pages

        :param game_name: Target game name
        :param request: Raw client request
        :return: Response with valid API options and respective links
        """
        parser = self.create_parser(game_name)
        return self.extract_valid_query_params(request.query_params, self.parse_table_of_content(parser))

    def extract_valid_query_params(self, request_query_params: QueryParams,
                                   table_of_content_data: Dict[str, List[Dict[str, str]]]) -> Dict:
        """
        Will validate whether the provided client query parameters are valid options for retrieving content options
        If valid will create pair of <Option Name> : <Content Link>
        Else ignore

        :param request_query_params: Raw request query parameters
        :param table_of_content_data: Target game table of content options
        :return: Dictionary with valid query parameters which have a corresponding content option
        """
        valid_query_params = {}

        for key, value in request_query_params.items():
            key_title = key.title()
            values = [temp.title() for temp in value.split(',')]
            if key_title in table_of_content_data.keys():
                for current in table_of_content_data[key_title]:
                    for source_key, source_link in current.items():
                        if source_key in values:
                            valid_query_params[source_key] = f"{GAME_WIKI_URL}{source_link}"
        return valid_query_params
