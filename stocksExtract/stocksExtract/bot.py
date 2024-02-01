from botcity.web import WebBot, Browser, By
from webdriver_manager.firefox import GeckoDriverManager
from botcity.web.parsers import table_to_dict
import pandas as pd
import os
import openpyxl


class Bot(WebBot):
    def action(self, execution=None):
        excel_filepath = 'stocks-now.xlsx'

        if os.path.exists(excel_filepath):
            os.remove(excel_filepath)
        
        wb = openpyxl.Workbook()
        wb.save(excel_filepath)

        self.headless = True
        self.browser = Browser.FIREFOX
        self.driver_path = GeckoDriverManager().install()

        print('Colecting data...')
        self.browse('https://www.fundamentus.com.br/buscaavancada.php')
        self.maximize_window()
        self.find_element('buscar', By.CLASS_NAME).click()
        self.wait(3000)

        table_element = self.find_element('resultado', By.ID)
        table_data = table_to_dict(table_element)

        self.stop_browser()

        df = pd.DataFrame(table_data)

        # Filter PL more than 3 and less than 10
        df = self.filter_df(df, 'pl', 3, 10)

        # Filter PVP more than 0.5 and less than 2
        df = self.filter_df(df, 'pvp', 0.5, 2)

        # Filter Dividend Yield more than 7% and less than 14%
        df = self.filter_df(df, 'divyield', 7, 14, True)

        # Filter ROE more than 15% and less than 30%
        df = self.filter_df(df, 'roe', 15, 30, True)

        # Filter Liquidez more than 1000000
        df = self.filter_df(df, 'liq2meses', 1000000, 1000000000000000000)

        # Sort by cotação
        df = df.sort_values(by='cotação', ascending=True)

        df.to_excel(excel_filepath, index=False)

        print('Process finished.')


    def filter_df(self, df, col, min, max, percent=False):
        df.loc[:, col] = df[col].str.replace('%', '')
        df.loc[:, col] = df[col].str.replace('.', '')
        df.loc[:, col] = df[col].str.replace(',', '.')
        df.loc[:, col] = df[col].astype(float)
        df = df[((df[col] > min) & (df[col] < max))]
        df.loc[:, col] = df[col].astype(str)
        df.loc[:, col] = df[col].str.replace('.', ',')
        if percent:
            df.loc[:, col] = df[col].apply(lambda x: f'{x} %')
        return df


if __name__ == '__main__':
    Bot.main()
