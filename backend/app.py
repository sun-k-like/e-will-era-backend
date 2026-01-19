from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os

app = FastAPI()

# 요청 데이터 구조 정의
class ProcessRequest(BaseModel):
    mode: str   # summarize, refine, validate 중 하나
    data: dict # original, refined 등의 텍스트 데이터

def get_prompt_template(mode, input_type):
    # 상위 폴더인 backend/prompts에서 파일 읽기
    file_path = f"prompts/{mode}_{input_type}.txt"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"프롬프트 파일을 찾을 수 없습니다: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

@app.post("/process")
async def process_text(request: ProcessRequest):
    try:
        # 1. 템플릿 로드 (예: prompts/validate_human.txt)
        template = get_prompt_template(request.mode, "human")
        
        # 2. 템플릿 치환 (동적 데이터 주입)
        # 템플릿 파일 내의 {original_text} 등을 실제 데이터로 교체합니다.
        final_prompt = template.format(
            original_text=request.data.get("original", "2025년도 에너지바우처 지원대상 확대. 주민등록표 등본상 세대주와의 관계가 자녀이면서 동시에 19세 미만인 사람을 2명 이상 포함하는 세대. 가정위탁아동은 자녀 수에 포함."),
            refined_text=request.data.get("refined", "2025년부터 19살 미만 아이가 2명 이상 있는 가정은 에너지바우처를 받을 수 있어요.")
        )
        
        # 3. 결과 반환 (내일은 여기서 Azure API를 호출하게 됩니다)
        return {
            "status": "success",
            "mode": request.mode,
            "final_prompt_to_be_sent": final_prompt,
            "message": "내일 Azure 키를 입력하면 이 프롬프트가 즉시 AI에게 전송됩니다."
        }
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"템플릿 변수 치환 오류: {str(e)}가 데이터에 없습니다.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)