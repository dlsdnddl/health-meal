import os
import urllib.parse

import streamlit as st
import google.generativeai as genai
import json
from dotenv import load_dotenv

def main():
    st.set_page_config(page_title="AI 맞춤형 질환 식단 & 장보기 서비스", page_icon="🥗", layout="centered")

    # 글로벌 스타일 (부드러운 그린/민트 계열, 모던 카드 UI - 2026 트렌드 반영)
    st.markdown(
        """
        <style>
            :root {
                --primary-bg: #f3fbf7;
                --primary: #34c29a;
                --primary-soft: #d6f4e7;
                --primary-dark: #17866a;
                --accent-yellow: #facc6b;
                --text-main: #0f172a;
                --text-sub: #6b7280;
                --card-bg: #ffffff;
                --shadow-soft: 0 18px 45px rgba(15, 118, 110, 0.13);
                --radius-lg: 18px;
            }

            html, body, [class*="css"]  {
                font-family: -apple-system, BlinkMacSystemFont, "Pretendard", system-ui, -system-ui,
                             "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans KR", sans-serif;
                background: radial-gradient(circle at top, #e9f9f1 0, #f3fbf7 40%, #f8fafc 100%);
                color: var(--text-main);
                font-size: 15px;
                -webkit-font-smoothing: antialiased;
                text-rendering: optimizeLegibility;
            }

            /* 메인 컨테이너 */
            .app-container {
                max-width: 960px;
                margin: 0 auto;
                padding: 1.6rem 1.1rem 3.2rem;
            }

            /* 헤더 영역 */
            .hero-header {
                position: relative;
                overflow: hidden;
                background: radial-gradient(circle at top left, #d9f7ea 0, #f4fbf6 45%, #ffffff 100%);
                border-radius: 26px;
                padding: 1.9rem 1.9rem 1.5rem;
                margin-bottom: 1.9rem;
                box-shadow: var(--shadow-soft);
                display: flex;
                flex-direction: column;
                gap: 0.6rem;
                border: 1px solid rgba(148, 163, 184, 0.18);
            }
            .hero-header::before {
                content: "";
                position: absolute;
                inset: 0;
                pointer-events: none;
                background: radial-gradient(circle at top right, rgba(250, 204, 21, 0.18), transparent 55%);
                opacity: 0.9;
            }
            .hero-title {
                font-size: 1.75rem;
                font-weight: 800;
                letter-spacing: -0.03em;
                display: flex;
                align-items: center;
                gap: 0.4rem;
                position: relative;
                z-index: 1;
            }
            .hero-pill {
                display: inline-flex;
                align-items: center;
                gap: 0.35rem;
                padding: 0.2rem 0.7rem;
                border-radius: 999px;
                background-color: rgba(76, 191, 156, 0.12);
                color: var(--primary-dark);
                font-size: 0.78rem;
                font-weight: 600;
                box-shadow: 0 8px 18px rgba(52, 194, 154, 0.2);
            }
            .hero-subtitle {
                font-size: 0.9rem;
                color: var(--text-sub);
                line-height: 1.7;
                max-width: 640px;
                position: relative;
                z-index: 1;
            }

            /* 입력 카드 */
            .input-card {
                background-color: var(--card-bg);
                border-radius: var(--radius-lg);
                padding: 1.3rem 1.25rem 1.1rem;
                box-shadow: 0 10px 30px rgba(15, 118, 110, 0.09);
                margin-bottom: 1.6rem;
                border: 1px solid rgba(148, 163, 184, 0.22);
                position: relative;
                overflow: hidden;
            }
            .input-card-title {
                font-size: 1.05rem;
                font-weight: 600;
                margin-bottom: 0.4rem;
                display: flex;
                align-items: center;
                gap: 0.35rem;
            }
            .input-card-desc {
                font-size: 0.86rem;
                color: var(--text-sub);
                margin-bottom: 0.6rem;
            }

            /* Streamlit 기본 입력 요소 여백 조정 */
            .input-card .stTextInput, .input-card .stButton {
                margin-top: 0.4rem;
            }

            /* 식단 결과 타이틀 */
            .plan-title {
                font-size: 1.2rem;
                font-weight: 700;
                margin: 1.7rem 0 0.55rem;
                display: flex;
                align-items: center;
                gap: 0.4rem;
            }

            /* 식단 카드 */
            .meal-card {
                background-color: var(--card-bg);
                border-radius: 20px;
                padding: 1.1rem 1.1rem 1rem;
                box-shadow: 0 16px 40px rgba(15, 118, 110, 0.12);
                border: 1px solid rgba(148, 163, 184, 0.2);
                margin-bottom: 1.1rem;
                transition: transform 0.12s ease-out, box-shadow 0.12s ease-out, border-color 0.12s ease-out;
            }
            .meal-card:hover {
                transform: translateY(-2px);
                box-shadow: 0 22px 55px rgba(15, 118, 110, 0.18);
                border-color: rgba(52, 194, 154, 0.45);
            }
            .meal-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 0.4rem;
            }
            .meal-time {
                font-size: 0.92rem;
                font-weight: 700;
                color: var(--primary-dark);
                display: inline-flex;
                align-items: center;
                gap: 0.3rem;
            }
            .meal-menu {
                font-size: 0.96rem;
                font-weight: 600;
                margin-bottom: 0.35rem;
            }
            .meal-ingredients-title {
                font-size: 0.84rem;
                font-weight: 600;
                color: var(--text-sub);
                margin-bottom: 0.15rem;
            }
            .meal-ingredients-list {
                font-size: 0.9rem;
                margin-bottom: 0.3rem;
            }

            /* 쿠팡 버튼 (HTML a 태그용) */
            .coupang-btn {
                display: inline-flex;
                align-items: center;
                justify-content: center;
                padding: 0.42rem 1rem;
                border-radius: 999px;
                border: none;
                background: linear-gradient(135deg, #4cbf9c, #3aa488);
                color: #ffffff !important;
                font-size: 0.83rem;
                font-weight: 600;
                text-decoration: none !important;
                box-shadow: 0 8px 18px rgba(15, 118, 110, 0.25);
                transition: transform 0.08s ease-out, box-shadow 0.12s ease-out, filter 0.12s ease-out;
                white-space: nowrap;
            }
            .coupang-btn:hover {
                transform: translateY(-1px);
                box-shadow: 0 12px 26px rgba(15, 118, 110, 0.3);
                filter: brightness(1.03);
            }
            .coupang-btn:active {
                transform: translateY(0);
                box-shadow: 0 6px 14px rgba(15, 118, 110, 0.22);
            }

            /* 반응형 */
            @media (max-width: 768px) {
                .app-container {
                    padding: 0.9rem 0.8rem 2.3rem;
                }
                .hero-header {
                    padding: 1.3rem 1.2rem 1.2rem;
                }
                .hero-title {
                    font-size: 1.35rem;
                }
                .meal-card {
                    padding: 0.95rem 0.9rem 0.9rem;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="app-container">
            <div class="hero-header">
                <div class="hero-pill">🥗 AI 맞춤형 질환 식단 & 장보기</div>
                <div class="hero-title">
                    건강 상태에 딱 맞는 1일 식단, AI가 제안해 드려요
                </div>
                <p class="hero-subtitle">
                    병명이나 건강 고민(예: 당뇨, 고혈압, 다이어트)을 입력하면,
                    의학·영양학적 근거를 바탕으로 아침·점심·저녁 식단과 장보기 목록을 한 번에 추천해 드립니다.
                </p>
            </div>
        """,
        unsafe_allow_html=True,
    )

    # .env에서 GEMINI_API_KEY 불러오기
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        st.error("서버 환경(.env)에 GEMINI_API_KEY가 설정되어 있지 않습니다. 관리자에게 문의해주세요.")
        return

    # 서버에서 자동으로 API 키 설정
    genai.configure(api_key=api_key)

    # 입력 카드
    st.markdown(
        """
        <div class="input-card">
            <div class="input-card-title">
                내 건강 상태 입력하기 💬
            </div>
            <div class="input-card-desc">
                예) 당뇨, 고혈압, 다이어트, 고지혈증, 위염, 관절 건강, 간 건강 등
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    user_health_condition = st.text_input("병명/건강상태를 입력해주세요", placeholder="예: 당뇨, 고혈압, 다이어트")

    if st.button("✨ AI에게 식단 추천받기", use_container_width=True):
        if user_health_condition:
            with st.spinner("AI가 식단을 분석 중입니다..."):
                try:
                        # Gemini API 호출 및 응답 처리 로직은 여기에 추가됩니다.
                        # 임시로 더미 데이터를 사용합니다.
                        model = genai.GenerativeModel('gemini-2.0-flash')
                        prompt = f"""
                            당신은 질환별 맞춤 식단 전문 영양사입니다. 사용자의 병명/건강상태에 맞춰 공감하는 메시지, 해당 식단이 좋은 이유에 대한 의학적/영양학적 근거, 아침/점심/저녁 1일 식단, 그리고 각 식단별 주요 재료 리스트를 JSON 형식으로 추천해주세요.

                            JSON 형식:
                            {{
                                "empathy": "사용자의 건강 상태에 대한 공감 메시지",
                                "reasoning": "식단이 좋은 의학적/영양학적 근거",
                                "meal_plan": [
                                    {{
                                        "time": "아침",
                                        "menu": "추천 메뉴",
                                        "ingredients": ["재료1", "재료2"]
                                    }},
                                    {{
                                        "time": "점심",
                                        "menu": "추천 메뉴",
                                        "ingredients": ["재료1", "재료2"]
                                    }},
                                    {{
                                        "time": "저녁",
                                        "menu": "추천 메뉴",
                                        "ingredients": ["재료1", "재료2"]
                                    }}
                                ]
                            }}

                            사용자의 병명/건강상태: {user_health_condition}
                            """
                        
                        response = model.generate_content(prompt)

                        # Gemini 응답을 우선 텍스트로 받고, JSON 파싱을 시도
                        response_text = getattr(response, "text", None)
                        if response_text is None:
                            # text 속성이 없을 경우 대비
                            try:
                                # 최신 google-generativeai 응답 구조 대비
                                response_text = "".join(
                                    part.text
                                    for part in response.candidates[0].content.parts
                                    if hasattr(part, "text")
                                )
                            except Exception:
                                response_text = str(response)

                        # Gemini가 ```json ... ``` 형태로 응답하는 경우 코드 블록 마크다운 제거
                        if response_text:
                            response_text = response_text.strip()
                            if response_text.startswith("```"):
                                # 앞의 ```json 또는 ``` 제거
                                response_text = response_text.lstrip("`")
                                # 첫 줄에 언어명이 붙어 있으면 제거
                                if response_text.lower().startswith("json"):
                                    response_text = response_text[4:]
                            # 끝쪽의 ``` 제거
                            if response_text.endswith("```"):
                                response_text = response_text[:-3]
                            response_text = response_text.strip()

                        try:
                            meal_data = json.loads(response_text)
                        except json.JSONDecodeError:
                            # JSON 파싱 실패 시, 원본 텍스트를 그대로 보여줌
                            st.error("AI 응답을 JSON으로 해석하지 못했습니다. 원문을 그대로 보여드릴게요.")
                            st.code(response_text)
                            return

                        st.markdown(
                            f"<div class='plan-title'>🧑‍🍳 '{user_health_condition}'에 대한 맞춤 1일 식단</div>",
                            unsafe_allow_html=True,
                        )

                        st.markdown(
                            f"<p style='font-size:0.9rem; color:#4b5563; margin-bottom:0.4rem;'><b>공감 메시지</b><br>{meal_data['empathy']}</p>",
                            unsafe_allow_html=True,
                        )
                        st.markdown(
                            f"<p style='font-size:0.9rem; color:#4b5563; margin-bottom:0.8rem;'><b>왜 이런 식단이 좋을까요?</b><br>{meal_data['reasoning']}</p>",
                            unsafe_allow_html=True,
                        )

                        for meal in meal_data['meal_plan']:
                            ingredients_html = ""
                            for ingredient in meal['ingredients']:
                                encoded_q = urllib.parse.quote_plus(str(ingredient))
                                coupang_link = (
                                    "https://www.coupang.com/np/search"
                                    f"?component=&q={encoded_q}&channel=user"
                                    "&eventCategory=SRP&eventLabel=coupang_partners"
                                    "&affiliate=dF7VYB"
                                )
                                ingredients_html += (
                                    f'<div style="display:flex; align-items:center; '
                                    f'justify-content:space-between; gap:0.6rem; margin-bottom:0.25rem;">'
                                    f'<span>{ingredient}</span>'
                                    f'<a class="coupang-btn" href="{coupang_link}" '
                                    f'target="_blank" rel="noopener noreferrer">쿠팡에서 구매</a>'
                                    f"</div>"
                                )

                            meal_html = (
                                f'<div class="meal-card">'
                                f'  <div class="meal-header">'
                                f'    <div class="meal-time">{meal["time"]} 🍽️</div>'
                                f"  </div>"
                                f'  <div class="meal-menu">{meal["menu"]}</div>'
                                f'  <div class="meal-ingredients-title">주요 재료</div>'
                                f'  <div class="meal-ingredients-list">{ingredients_html}</div>'
                                f"</div>"
                            )
                            st.markdown(meal_html, unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"오류가 발생했습니다: {e}")
        else:
            st.warning("병명/건강상태를 입력해주세요.")

    # 쿠팡 파트너스 고지 문구 (페이지 맨 아래, 작은 회색 글씨)
    st.markdown(
        """
        <p style="font-size: 12px; color: #888888; text-align: center; margin-top: 2rem;">
        이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다.
        </p>
        </div>  <!-- .app-container -->
        """,
        unsafe_allow_html=True,
    )

if __name__ == "__main__":
    main()
