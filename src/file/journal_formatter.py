from typing import *
from src.utils.utils import replace_occurrences
from src.utils.format_vars import LINK_FORMATS, FOOTER_FORMATS, SORTABLE_CONTENT, LINKABLE_CONTENT, \
    COLUMN_DESCRIPTIONS, TABLE_TITLE_KEYWORD, LINK_ID_KEYWORD, LINE_PARAGRAPH_SIZE
from src.utils.utils import extract_format_arguments, unwrap_css_classes
from datetime import datetime

def tagged(tag):
    def decorator(func):
        func._tag = tag
        return func
    return decorator

class JournalFormatter:
    def __init__(self,
                 timeframe: str,
                 date: str,
                 exchange: str,
                 pnl: float,
                 links: List,
                 display_order: List,
                 format_style: str):

        self.timeframe = timeframe
        self.date = date
        self.creation_date = datetime.today().strftime('%Y-%m-%d')
        self.exchange = exchange
        self.pnl = pnl
        self.available_links = links
        self.display_order = display_order
        self.style = format_style

        self.properties = ""
        self.links = []
        self.charts = []
        self.tables = []
        self.tags = ""
        self.footer = {link: [] for link in LINKABLE_CONTENT}

        self.build_links()

    def get_default_title_details(self):
        return {
            "timeframe": self.timeframe,
            "date": self.date,
            "pnl": f"({'+' + str(self.pnl) if self.pnl > 0.0 else str(self.pnl)}%)"
        }

    def get_default_properties(self):
        return {
            "Timeframe": self.timeframe,
            "Exchange": self.exchange,
            "Profitable": "true" if self.pnl > 0.0 else "false",
            "DateCreated": self.creation_date,
            "DateUpdated": self.creation_date,
        }

    def format_title(self, title_template: str):
        formattable_args = extract_format_arguments(title_template)
        title_info = self.get_default_title_details()
        requested_args = {arg: title_info.get(arg, '') for arg in formattable_args}

        return title_template.format_map(requested_args)

    def serialize_dataview_model(self, df):
        df_colnames = list(df.columns.values)
        #dict_content = df.to_dict('records')
        max_lengths = {}

        for column in df.columns:
            # + 2  # added 2 to account for white spaces between words
            header_length = len(column)
            max_cell_length = df[column].astype(str).map(len).max()
            max_lengths[column] = max(header_length, max_cell_length)

        #table_header = f"| {' | '.join(df_colnames)} |"
        table_header = []
        separator_row = []

        for colname in df_colnames:
            # build table_header
            table_header += self.format_table_cell(colname, max_lengths[colname], 'header')
            # build separator_row
            separator_row += self.format_table_cell("", max_lengths[colname], 'separator')

        table_header = self.format_table_row(table_header)
        separator_row = self.format_table_row(separator_row)
        table_content = self.construct_markdown_padded_table(df)


    def format_table_cell(self, label, max_length, cell_type):
        len_diff = abs(max_length - len(label))
        formatted_cell = ''
        char_filler = ''
        if cell_type == 'header' or  cell_type == 'content':
            char_filler = ' '
        elif cell_type == 'separator':
            char_filler = '-'
        else:
            char_filler = ' '

        return f' {label + (char_filler * len_diff)} '


    def __format_table_row(self, row_content):
        return f"|{'|'.join(row_content)}|"


    def __build_column_descriptions(self, table_title, df_colnames):
        descriptions = '\n'.join(
            [f'    - **{col}** - {COLUMN_DESCRIPTIONS.get(col, "")};' for col in df_colnames]

        )
        return (replace_occurrences(FOOTER_FORMATS.get("tables"), TABLE_TITLE_KEYWORD, table_title)
                + '\n' + descriptions)


    def build_table(self, table_title, df, links_enabled):
        # maximum character length for each column, including the header
        df_colnames =  df.columns.to_series()
        max_lengths = df_colnames.map(len).combine(
            df.astype(str).map(len).max(), max
        )

        # pad each cell to the column's maximum length
        def padd_row(row, is_header=False):
            return '| ' + ' | '.join(
                f"{str(value):<{max_lengths.iloc[i]}}"
                for i, value in enumerate(row)
            ) + ' |'

        header = padd_row(df.columns, is_header=True)

        separator = '| ' + ' | '.join('-' * max_lengths.iloc[i] for i in range(len(df.columns))) + ' |'

        rows = df.apply(padd_row, axis=1).tolist()

        # combine title, header, separator, and rows into the final table + attach column description
        col_description = ''
        if links_enabled:
            col_description = LINK_FORMATS.get("tables")
            self.footer['tables'] += [self.__build_column_descriptions(table_title, list(df_colnames))]

        table_content = f"# {table_title}" +  f"\n{col_description}\n\n" + '\n'.join([header, separator] + rows)

        #self.tables += [table_content]
        return table_content

    @tagged("tables")
    def build_tables(self, df_to_journal):
        self.tables = '\n\n'.join([self.build_table(df_dict.get('title'), df_dict.get('content'),  df_dict.get('descriptions'))
         for df_dict in df_to_journal])

    @tagged("charts")
    def build_charts(self, charts_to_journal):
        # TODO extend for other types of charts
        self.charts = '\n'.join([self.build_chart(*chart) for chart in charts_to_journal])

    def build_chart(self,
                    chart_title: str,
                    pie_data: List[Tuple],
                    chart_template: Dict,
                    color_schemes: Dict,
                    type: str = 'pie'):
        if not pie_data:
            print("No data was provided to generate the pie chart. Skipping this step.")
            return

        # This is currently being done because the mermaid's Pie Chart themeVariables indexes are inversely related
        # to the label's quantity (a "higher" label gets associated with first color scheme aka 'pie1' and so on)
        pie_data_sorted = sorted(pie_data, reverse=True, key=lambda tupl: tupl[1])

        chart_content = []
        theme_vars = {}
        pie_var_name = "pie"
        for pie_id, tupl in enumerate(pie_data_sorted):
            label = tupl[0]
            quant = tupl[1]
            color_scheme = color_schemes.get(label, "Default")
            quantified_label = f'"{label} ({quant})": {quant}'

            theme_vars[pie_var_name + str(pie_id+1)] = color_scheme
            chart_content += [quantified_label]

        chart_content = '\n'.join(chart_content)
        theme_vars = str(theme_vars)

        #self.charts += [chart_template.get(self.style).format(theme_vars_dict=theme_vars,
        #                                      chart_title=chart_title,
        #                                      label_to_value_map=chart_content)]
        return chart_template.get(self.style).format(theme_vars_dict=theme_vars,
                                              chart_title=chart_title,
                                              label_to_value_map=chart_content)

    #@tagged("properties")
    def build_properties(self, css_classes, properties_requested):
        properties_info = {}
        if properties_requested:
            default_properties = self.get_default_properties()
            properties_info = {arg: default_properties.get(arg, '') for arg in properties_requested}

        if css_classes:
            inline_css_classes = unwrap_css_classes(css_classes)
            properties_info["cssclasses"] = inline_css_classes

        self.properties = "---\n" + '\n'.join([f"{property_name}: {property_info}"
                                     for property_name, property_info in properties_info.items()]) + "\n---"

    @tagged("links")
    def build_links(self):
        if self.available_links and "links" in self.display_order:
            self.links = LINK_FORMATS.get("links")

            footer_links = []
            if self.pnl > 0:
                wins_link = self.available_links.get("win")
                if wins_link:
                    footer_links += [wins_link]
            elif self.pnl < 0:
                losses_link = self.available_links.get("loss")
                if losses_link:
                    footer_links += [losses_link]
            # expand links here if necessary

        self.footer["links"] += [(FOOTER_FORMATS.get("links") +
                                '\n' + '\n'.join(f"    - [[{link}]]" for link in footer_links))]

    @tagged("tags")
    def build_tags(self, tags: List):
        self.tags = '\n'.join(f"#{tag}" for tag in tags)

    # get exchange_name

    def build_journal_ordered(self, journal_template):
        journal_attrs = vars(self)
        content = []
        footer_content = []
        link_pos = 1
        for element in self.display_order:
            if element in journal_attrs and element in SORTABLE_CONTENT:
                if element in LINKABLE_CONTENT:
                    footer_element = self.footer.get(element)
                    if type(footer_element) == list:
                        replaced_content = replace_occurrences(journal_attrs.get(element), LINK_ID_KEYWORD,
                                                               range(link_pos, link_pos + len(footer_element)))
                        replaced_footer_content = '\n'.join([replace_occurrences(el, LINK_ID_KEYWORD, link_pos + pos)
                                                   for pos, el in enumerate(footer_element)])
                        link_pos += len(footer_element)
                    elif type(footer_element) == str:
                        replaced_content = replace_occurrences(journal_attrs.get(element), LINK_ID_KEYWORD, link_pos)
                        replaced_footer_content = replace_occurrences(footer_element, LINK_ID_KEYWORD, link_pos)
                        link_pos += 1
                    else:
                        raise Exception(f"Unsupported footer element type '{type(footer_element)}' found while formatting"
                                        f" the journal build.")
                    content += [replaced_content] if replaced_content else content
                    footer_content += [replaced_footer_content] if replaced_footer_content else footer_element
                else:
                    content += [journal_attrs.get(element)]

        return journal_template.get(self.style).format(
            properties=self.properties,
            content=('\n' * LINE_PARAGRAPH_SIZE.get("content")).join(content),
            tags=self.tags,
            footer=('\n' * LINE_PARAGRAPH_SIZE.get("footer")).join(footer_content)
        )
