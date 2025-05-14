from bs4 import BeautifulSoup
import requests
import json

class Gemini_token_limits():
    def __init__(self):
        self.url = "https://ai.google.dev/gemini-api/docs/models"
        self.response = requests.get(self.url)
        self.response.raise_for_status()
        self.soup = BeautifulSoup(self.response.text, "html.parser")

    def extract_model_info(self, section):
        model_info = {}
        
        # モデル名を取得（devsite-expandableのidから）
        model_id = section.get('id', '')
        model_info['id'] = model_id
        
        # Token limitsを探す
        for tr in section.find_all("tr"):
            td = tr.find("td")
            if td and "Token limits" in td.text:
                sections = tr.find_all("section")
                for section in sections:
                    # Input token limit
                    b_input = section.find("b", string="Input token limit")
                    if b_input:
                        ps = section.find_all("p")
                        if len(ps) >= 2:
                            value = ps[1].text.strip()
                            try:
                                model_info['input_token_limit'] = int(value.replace(',', ''))
                            except ValueError:
                                model_info['input_token_limit'] = None
                    
                    # Output token limit
                    b_output = section.find("b", string="Output token limit")
                    if b_output:
                        ps = section.find_all("p")
                        if len(ps) >= 2:
                            value = ps[1].text.strip()
                            try:
                                model_info['output_token_limit'] = int(value.replace(',', ''))
                            except ValueError:
                                model_info['output_token_limit'] = None
                break

        # Versions行を探す
        versions_tr = None
        for tr in section.find_all("tr"):
            td = tr.find("td")
            if td and "Versions" in td.text:
                versions_tr = tr
                break

        if versions_tr:
            ul = versions_tr.find("ul")
            if ul:
                versions = {}
                for li in ul.find_all("li"):
                    label = li.text.split(":")[0].strip()
                    code = li.find("code")
                    value = code.text.strip() if code else ""
                    versions[label] = value
                model_info['versions'] = versions

        return model_info

    def extract_all_models(self, rate_limits=None):
        # すべてのdevsite-expandableを取得
        model_sections = self.soup.find_all("devsite-expandable")
        
        # 結果を格納する辞書
        result = {}
        
        for section in model_sections:
            model_info = self.extract_model_info(section)
            model_id = model_info.pop('id')  # idをキーとして使用するため、辞書から削除
            
            # token limitsのみを含む新しい辞書を作成
            limits = {}
            if 'input_token_limit' in model_info and isinstance(model_info['input_token_limit'], int):
                limits['input_token_limit'] = model_info['input_token_limit']
            if 'output_token_limit' in model_info and isinstance(model_info['output_token_limit'], int):
                limits['output_token_limit'] = model_info['output_token_limit']
            
            if limits:  # token limitsが存在する場合のみ追加
                result[model_id] = limits

        # レート制限情報がある場合、マージする
        if rate_limits:
            merged_result = {}
            for tier, models in rate_limits.items():
                merged_result[tier] = {}
                for model_name, rate_info in models.items():
                    # モデル名を小文字に変換し、スペースをハイフンに置換
                    model_key = model_name.lower().replace(" ", "-")
                    if model_key in result:
                        merged_result[tier][model_name] = {
                            **rate_info,
                            **result[model_key],
                            "extra-info": {}
                        }
            return merged_result
        
        return result

if __name__ == "__main__":
    gemini_info_rate_limits = Gemini_info_rate_limits()
    gemini_info_rate_limits.extract_all_models() 