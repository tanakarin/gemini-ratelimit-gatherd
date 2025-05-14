from gemini_rate_limit import Gemini_rate_limit
from gemini_token_limits import Gemini_token_limits
import json

class GeminiModelInfoComposite:
    """
    Gemini_info_rate_limitsクラスとGemini_rate_limitクラスをコンポジションとして持つクラス
    """
    def __init__(self):
        self.rate_limits = Gemini_rate_limit()
        self.model_info = Gemini_token_limits()

    def get_all_info(self):
        """
        レート制限とモデル情報を統合して取得する
        """
        # レート制限情報を取得
        rate_limits = {}
        tiers = ['free', '1', '2', '3']
        for tier in tiers:
            result = self.rate_limits.extract_gemini_info(tier)
            if result:
                rate_limits[f"tier-{tier}"] = result

        # モデル情報を取得し、レート制限情報とマージ
        merged_info = self.model_info.extract_all_models(rate_limits)

        return merged_info

    def print_all_info(self):
        """
        統合された情報をJSON形式で出力する
        """
        result = self.get_all_info()
        print(json.dumps(result, indent=4, ensure_ascii=False))

    def save_json(self, filename="gemini_models.json"):
        """
        統合された情報をJSONファイルに保存する
        """
        result = self.get_all_info()
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    gemini_model_info = GeminiModelInfoComposite()
    gemini_model_info.print_all_info()
    gemini_model_info.save_json() 