from utils.ai import analyze_doc
import json


class InvestmentsAnalayzer:
    def __init__(self, fd):
        self.fd = fd
        self.json = None

    def analyze(self, on_done):
        docs_types = "(statement or distribution or wire or capital call or commitment)"
        distribution_ai = "return a json with the following keys \
                    (fund_name, title, current_value (the distribution, without commas), report_date,\
                        doc_type, currency, period_date), if 'period_date' or 'report_date' not found, fill one with the other"
        statement_ai = "return a json with the following keys \
                    (fund_name, title, current_value (without commas in integer or float), report_date,\
                        period_date, doc_type, initial_investment, currency)"
        wire_ai = "return a json with the following keys \
                    (fund_name, title, current_value (without commas and without dot), report_date,\
                        doc_type, currency)"
        general_ai_info = f"in most cases 'fund_name' is in the first row of the title, 'doc_type' can be on of {docs_types} and in most cases is in the title"
        general_ai_info += ", return a valid json (without comments like \\)"
        ai_text = f"if it is a 'statement' {statement_ai},\
            if it is a 'distribution' {distribution_ai}, \
            if it is a 'Wire Receipt' or 'Capital call' {wire_ai}, {general_ai_info}"
        ai_text = f"{distribution_ai}, {general_ai_info}"
        ret = analyze_doc(ai_text, file_path=None, fd=self.fd)
        self.on_analyze_done(ret, on_done)
        return ret

    def on_analyze_done(self, result, on_done):
        # print("on_analyze_done", analyzed_result)
        json_index_start = result.find("```json") + len("```json")
        json_index_end = result.find("```", json_index_start+5)
        try:
            self.json = json.loads(
                result[json_index_start:json_index_end-1])
        except Exception as e:
            print("load failed", e)
            print(result, json_index_start, json_index_end)
            print(result[json_index_start:json_index_end-2])
            return
        print("Ai json", json.dumps(self.json, indent=4))
        watcher_name = self.get_watcher_name_from_json_ai()
        print(f'{watcher_name=}')
        self.json["watcher_name"] = watcher_name
        on_done(self.json)

    def get_watcher_name_from_json_ai(self):
        if "fund_name" in self.json:
            return self.json["fund_name"]

        json_list_names = ["founds", "fund_details", "found"]
        for name in json_list_names:
            if name in self.json:
                for f_json in self.json[name]:
                    if f_json["current_value"]:
                        return f_json["fund_name"]

        for f_json in self.json:
            if f_json["current_value"]:
                return f_json["fund_name"]

        return None
