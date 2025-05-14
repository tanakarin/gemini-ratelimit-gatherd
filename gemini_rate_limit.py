import requests
import argparse
import json
from bs4 import BeautifulSoup

# 定数定義
INT_MAX = 2147483647  # 32ビット整数の最大値

class Gemini_rate_limit():
    def __init__(self):
        self.url = "https://ai.google.dev/gemini-api/docs/rate-limits#free-tier"
        self.response = requests.get(self.url)
        self.response.raise_for_status()
        self.soup = BeautifulSoup(self.response.text, "html.parser")

    def extract_gemini_info(self, tier):
        tier_id = f'tier-{tier}' if tier != 'free' else 'free-tier'
        tier_section = self.soup.find('h3', {'id': tier_id})
        if not tier_section:
            print(f"Tier {tier}のセクションが見つかりませんでした。")
            return None

        # セクション内のテーブルを探す
        table = tier_section.find_next('table')
        if not table:
            print(f"Tier {tier}のテーブルが見つかりませんでした。")
            return None

        # 結果を格納する辞書
        result = {}

        # テーブルの各行を処理（ヘッダー行をスキップ）
        for row in table.find_all('tr')[1:]:
            columns = row.find_all('td')
            if len(columns) >= 4:
                model = columns[0].text.strip().replace(" ", "-")
                rpm = columns[1].text.strip()
                tpm = columns[2].text.strip()
                rpd = columns[3].text.strip()
                
                # rpm,tpmが--の場合、rpm,tpm,rpdを-1に設定
                if rpm == "--" and tpm == "--":
                    rpm = -1
                    tpm = -1
                    rpd = -1
                # rpmまたはtpmが--でない場合、tpm,rpdが--の場合はINT_MAXに設定
                elif rpm != "--" or tpm != "--":
                    if tpm == "--":
                        tpm = INT_MAX
                    if rpd == "--":
                        rpd = INT_MAX
                    # 数値に変換
                    try:
                        rpm = int(rpm.replace(',', ''))
                    except ValueError:
                        rpm = None
                    try:
                        if isinstance(tpm, str):
                            tpm = int(tpm.replace(',', ''))
                    except ValueError:
                        tpm = None
                    try:
                        if isinstance(rpd, str):
                            rpd = int(rpd.replace(',', ''))
                    except ValueError:
                        rpd = None
                
                # rpm, tpm, rpdがintでない場合はスキップ
                if not (isinstance(rpm, int) and isinstance(tpm, int) and isinstance(rpd, int)):
                    continue
                
                result[model] = {
                    'rpm': rpm,
                    'tpm': tpm,
                    'rpd': rpd
                }

        return result

    def extract_all_tiers(self):
        tiers = ['free', '1', '2', '3']
        all_results = {}
        for tier in tiers:
            result = self.extract_gemini_info(tier)
            if result:
                all_results[f"tier-{tier}"] = result
        return all_results

def main():
    gemini_rate_limit = Gemini_rate_limit()
    gemini_rate_limit.extract_all_tiers()
    print(json.dumps(gemini_rate_limit.extract_all_tiers(), indent=4, ensure_ascii=False))

if __name__ == "__main__":
    main() 