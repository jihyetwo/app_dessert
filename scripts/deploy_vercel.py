#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Vercel REST API를 통한 app-dessert 프로젝트 생성 및 자동 배포 스크립트.
토큰은 로컬 auth.json 또는 VERCEL_TOKEN 환경변수에서 동적으로 로드합니다.
"""

import os
import sys
import json
import urllib.request
import urllib.error

PROJECT_NAME = "app-dessert"
REPO = "jihyetwo/app_dessert"
DEFAULT_TEAM_ID = "team_jEzrvblcr1zAi7UqiphiZ4Vi"

def get_credentials():
    """로컬 Vercel 설정 또는 환경변수에서 토큰과 팀 ID 로드"""
    token = os.environ.get("VERCEL_TOKEN")
    team_id = os.environ.get("VERCEL_TEAM_ID")

    home = os.path.expanduser("~")
    auth_file = os.path.join(home, "Library", "Application Support", "com.vercel.cli", "auth.json")
    config_file = os.path.join(home, "Library", "Application Support", "com.vercel.cli", "config.json")

    if not token and os.path.exists(auth_file):
        try:
            with open(auth_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                token = data.get("token")
        except Exception:
            pass

    if not team_id and os.path.exists(config_file):
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                team_id = data.get("currentTeam")
        except Exception:
            pass

    return token, team_id or DEFAULT_TEAM_ID

def api_call(endpoint, method="GET", data=None, token=None, team_id=None):
    url = f"https://api.vercel.com{endpoint}"
    if "?" in url:
        url += f"&teamId={team_id}"
    else:
        url += f"?teamId={team_id}"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    req_data = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req) as res:
            res_body = res.read().decode("utf-8")
            return json.loads(res_body) if res_body else {}
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        try:
            return {"error": json.loads(err_body), "code": e.code}
        except:
            return {"error": err_body, "code": e.code}
    except Exception as e:
        return {"error": str(e)}

def deploy():
    token, team_id = get_credentials()
    if not token:
        print("❌ Vercel 인증 토큰을 찾을 수 없습니다. (auth.json 또는 VERCEL_TOKEN 확인)")
        return False

    # 프로젝트 확인 및 생성
    projects_res = api_call("/v9/projects", token=token, team_id=team_id)
    existing_project = None
    if "projects" in projects_res:
        for p in projects_res["projects"]:
            if p.get("name") == PROJECT_NAME:
                existing_project = p
                break

    if not existing_project:
        api_call("/v9/projects", method="POST", data={"name": PROJECT_NAME}, token=token, team_id=team_id)

    # index.html 직접 업로드 배포
    index_path = "/Users/name/cursor/app/index.html"
    if not os.path.exists(index_path):
        print("❌ index.html 파일이 존재하지 않습니다.")
        return False

    with open(index_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    upload_payload = {
        "name": PROJECT_NAME,
        "files": [
            {
                "file": "index.html",
                "data": html_content
            },
            {
                "file": "vercel.json",
                "data": json.dumps({"version": 2, "cleanUrls": True, "trailingSlash": False})
            }
        ],
        "projectSettings": {
            "framework": None
        }
    }
    upload_res = api_call("/v13/deployments", method="POST", data=upload_payload, token=token, team_id=team_id)

    if "url" in upload_res:
        deploy_url = f"https://{upload_res['url']}"
        prod_url = f"https://{PROJECT_NAME}.vercel.app"
        print(f"🎉 Vercel 배포 성공!")
        print(f"   ├─ 배포 URL: {deploy_url}")
        print(f"   └─ 프로덕션 도메인: {prod_url}")
        return True
    else:
        print(f"⚠️ Vercel 배포 응답: {upload_res}")
        return False

if __name__ == "__main__":
    deploy()
