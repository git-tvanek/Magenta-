#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MagentaTV API Client

Klient pro komunikaci s API služby Magenta TV / Magio TV.
"""
import os
import json
import time
import uuid
import requests
from urllib.parse import urlparse
from datetime import datetime, timedelta
import logging
from flask import current_app

logger = logging.getLogger(__name__)


class MagentaTV:
    def __init__(self, username, password, language="cz", quality="p5"):
        """
        Inicializace MagentaTV API klienta
        
        Args:
            username (str): Přihlašovací jméno
            password (str): Heslo
            language (str): Kód jazyka (cz, sk)
            quality (str): Kvalita streamu (p1-p5, kde p5 je nejvyšší)
        """
        self.username = username
        self.password = password
        self.language = language.lower()
        self.quality = quality
        
        # URL podle jazyka
        self.base_url = f"https://{self.language}go.magio.tv"
        
        # User-Agent
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 MagioGO/4.0.21"
        
        # Session pro HTTP požadavky
        self.session = requests.Session()
        
        # Informace o zařízení
        self.device_id = str(uuid.uuid4())
        self.device_name = "Web Client"
        self.device_type = "OTT_WIN"
        
        # Tokeny
        self.access_token = None
        self.refresh_token = None
        self.token_expires = 0
        
        # Soubor pro uložení přihlašovacích údajů
        self.token_file = os.path.join(current_app.config["DATA_DIR"], f"token_{language}.json")
        
        # Načtení tokenů při inicializaci
        self._load_tokens()

    def _load_tokens(self):
        """Načtení tokenů ze souboru"""
        if os.path.exists(self.token_file):
            try:
                with open(self.token_file, 'r') as f:
                    data = json.load(f)
                    self.access_token = data.get("access_token")
                    self.refresh_token = data.get("refresh_token")
                    self.token_expires = data.get("expires", 0)
                    self.device_id = data.get("device_id", self.device_id)
                logger.info("Tokeny načteny ze souboru")
            except Exception as e:
                logger.error(f"Chyba při načítání tokenů: {e}")

    def _save_tokens(self):
        """Uložení tokenů do souboru"""
        try:
            with open(self.token_file, 'w') as f:
                json.dump({
                    "access_token": self.access_token,
                    "refresh_token": self.refresh_token,
                    "expires": self.token_expires,
                    "device_id": self.device_id
                }, f)
            logger.info("Tokeny uloženy do souboru")
        except Exception as e:
            logger.error(f"Chyba při ukládání tokenů: {e}")

    def login(self):
        """
        Přihlášení k službě MagentaTV
        
        Returns:
            bool: True v případě úspěšného přihlášení, jinak False
        """
        # Ověření platnosti současného tokenu
        if self.refresh_token and self.token_expires > time.time() + 60:
            logger.info("Současný token je stále platný")
            return self.refresh_access_token()
            
        # Parametry pro inicializaci přihlášení
        params = {
            "dsid": self.device_id,
            "deviceName": self.device_name,
            "deviceType": self.device_type,
            "osVersion": "0.0.0",
            "appVersion": "4.0.21-hf.0",
            "language": self.language.upper(),
            "devicePlatform": "GO"
        }
        
        headers = {
            "Host": f"{self.language}go.magio.tv",
            "User-Agent": self.user_agent
        }
        
        try:
            # První požadavek na inicializaci přihlášení
            init_response = self.session.post(
                f"{self.base_url}/v2/auth/init",
                params=params,
                headers=headers,
                timeout=30
            ).json()
            
            if not init_response.get("success", False):
                error_msg = init_response.get('errorMessage', 'Neznámá chyba')
                logger.error(f"Chyba inicializace: {error_msg}")
                return False
            
            # Získání dočasného přístupového tokenu
            temp_access_token = init_response["token"]["accessToken"]
            
            # Parametry pro přihlášení s uživatelským jménem a heslem
            login_params = {
                "loginOrNickname": self.username,
                "password": self.password
            }
            
            login_headers = {
                "Content-type": "application/json",
                "Authorization": f"Bearer {temp_access_token}",
                "Host": f"{self.language}go.magio.tv",
                "User-Agent": self.user_agent
            }
            
            # Požadavek na přihlášení
            login_response = self.session.post(
                f"{self.base_url}/v2/auth/login",
                json=login_params,
                headers=login_headers,
                timeout=30
            ).json()
            
            if not login_response.get("success", False):
                error_msg = login_response.get('errorMessage', 'Neznámá chyba')
                logger.error(f"Chyba přihlášení: {error_msg}")
                return False
            
            # Uložení přihlašovacích tokenů
            self.access_token = login_response["token"]["accessToken"]
            self.refresh_token = login_response["token"]["refreshToken"]
            self.token_expires = time.time() + login_response["token"]["expiresIn"] / 1000
            
            # Uložení tokenů do souboru
            self._save_tokens()
            
            logger.info("Přihlášení úspěšné")
            return True
            
        except Exception as e:
            logger.error(f"Chyba při přihlášení: {e}")
            return False

    def refresh_access_token(self):
        """
        Obnovení přístupového tokenu pomocí refresh tokenu
        
        Returns:
            bool: True v případě úspěšného obnovení tokenu, jinak False
        """
        if not self.refresh_token:
            logger.warning("Refresh token není k dispozici, je nutné se znovu přihlásit")
            return self.login()
        
        # Kontrola vypršení tokenu
        if self.token_expires > time.time() + 60:
            return True
            
        params = {
            "refreshToken": self.refresh_token
        }
        
        headers = {
            "Content-type": "application/json",
            "Host": f"{self.language}go.magio.tv",
            "User-Agent": self.user_agent
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/v2/auth/tokens",
                json=params,
                headers=headers,
                timeout=30
            ).json()
            
            if not response.get("success", False):
                error_msg = response.get('errorMessage', 'Neznámá chyba')
                logger.error(f"Chyba obnovení tokenu: {error_msg}")
                return self.login()
                
            self.access_token = response["token"]["accessToken"]
            self.refresh_token = response["token"]["refreshToken"]
            self.token_expires = time.time() + response["token"]["expiresIn"] / 1000
            
            # Uložení tokenů do souboru
            self._save_tokens()
            
            logger.info("Token úspěšně obnoven")
            return True
            
        except Exception as e:
            logger.error(f"Chyba při obnovení tokenu: {e}")
            return self.login()

    def get_channels(self):
        """
        Získání seznamu dostupných kanálů
        
        Returns:
            list: Seznam kanálů s jejich ID, názvem, logem a kategorií
        """
        if not self.refresh_access_token():
            return []
            
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Host": f"{self.language}go.magio.tv",
            "User-Agent": self.user_agent
        }
        
        try:
            # Získání kategorií pro kanály
            categories_response = self.session.get(
                f"{self.base_url}/home/categories",
                params={"language": self.language},
                headers=headers,
                timeout=30
            ).json()
            
            categories = {}
            for category in categories_response.get("categories", []):
                for channel in category.get("channels", []):
                    categories[channel["channelId"]] = category["name"]
            
            # Získání seznamu kanálů
            params = {
                "list": "LIVE",
                "queryScope": "LIVE"
            }
            
            channels_response = self.session.get(
                f"{self.base_url}/v2/television/channels",
                params=params,
                headers=headers,
                timeout=30
            ).json()
            
            if not channels_response.get("success", True):
                logger.error("Chyba při získání kanálů")
                return []
                
            channels = []
            for item in channels_response.get("items", []):
                channel = item.get("channel", {})
                channel_id = channel.get("channelId")
                
                channels.append({
                    "id": channel_id,
                    "name": channel.get("name", ""),
                    "original_name": channel.get("originalName", ""),
                    "logo": channel.get("logoUrl", ""),
                    "group": categories.get(channel_id, "Ostatní"),
                    "has_archive": channel.get("hasArchive", False)
                })
                
            return channels
            
        except Exception as e:
            logger.error(f"Chyba při získání kanálů: {e}")
            return []

    def get_stream_url(self, channel_id):
        """
        Získání URL pro streamování kanálu
        
        Args:
            channel_id (int): ID kanálu
            
        Returns:
            dict: Informace o streamu včetně URL nebo None v případě chyby
        """
        if not self.refresh_access_token():
            return None
            
        params = {
            "service": "LIVE",
            "name": self.device_name,
            "devtype": self.device_type,
            "id": int(channel_id),
            "prof": self.quality,
            "ecid": "",
            "drm": "widevine",
            "start": "LIVE",
            "end": "END",
            "device": "OTT_PC_HD_1080p_v2"
        }
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Host": f"{self.language}go.magio.tv",
            "User-Agent": self.user_agent,
            "Accept": "*/*",
            "Referer": f"https://{self.language}go.magio.tv/"
        }
        
        try:
            response = self.session.get(
                f"{self.base_url}/v2/television/stream-url",
                params=params,
                headers=headers,
                timeout=10
            ).json()
            
            if not response.get("success", False):
                error_msg = response.get('errorMessage', 'Neznámá chyba')
                logger.error(f"Chyba při získání stream URL: {error_msg}")
                return None
                
            url = response["url"]
            
            # Následování přesměrování pro získání skutečné URL
            headers_redirect = {
                "Host": urlparse(url).netloc,
                "User-Agent": self.user_agent,
                "Authorization": f"Bearer {self.access_token}",
                "Accept": "*/*",
                "Referer": f"https://{self.language}go.magio.tv/"
            }
            
            redirect_response = self.session.get(
                url,
                headers=headers_redirect,
                allow_redirects=False,
                timeout=10
            )
            
            final_url = redirect_response.headers.get("location", url)
            
            # Vrátíme informace o streamu
            return {
                "url": final_url,
                "headers": dict(headers_redirect),
                "content_type": redirect_response.headers.get("Content-Type", "application/vnd.apple.mpegurl"),
                "is_live": True
            }
            
        except Exception as e:
            logger.error(f"Chyba při získání stream URL: {e}")
            return None

    def get_epg(self, channel_id=None, days_back=1, days_forward=1):
        """
        Získání EPG (Electronic Program Guide) pro zadaný kanál nebo všechny kanály
        
        Args:
            channel_id (int, optional): ID kanálu nebo None pro všechny kanály
            days_back (int): Počet dní zpět
            days_forward (int): Počet dní dopředu
            
        Returns:
            dict: EPG data rozdělená podle kanálů nebo None v případě chyby
        """
        if not self.refresh_access_token():
            return None
            
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Host": f"{self.language}go.magio.tv",
            "User-Agent": self.user_agent
        }
        
        # Časový rozsah pro EPG
        current_date = datetime.now()
        start_time = (current_date - timedelta(days=days_back)).strftime("%Y-%m-%dT00:00:00.000Z")
        end_time = (current_date + timedelta(days=days_forward)).strftime("%Y-%m-%dT23:59:59.000Z")
        
        # Vytvoření filtru podle toho, zda je zadáno ID kanálu
        if channel_id:
            filter_str = f"channel.id=={channel_id} and startTime=ge={start_time} and endTime=le={end_time}"
        else:
            # Získat seznam všech kanálů
            channels = self.get_channels()
            if not channels:
                return None
                
            channel_ids = [str(channel["id"]) for channel in channels]
            filter_str = f"channel.id=in=({','.join(channel_ids)}) and startTime=ge={start_time} and endTime=le={end_time}"
        
        params = {
            "filter": filter_str,
            "limit": 1000,
            "offset": 0,
            "lang": self.language.upper()
        }
        
        try:
            response = self.session.get(
                f"{self.base_url}/v2/television/epg",
                params=params,
                headers=headers,
                timeout=30
            ).json()
            
            if not response.get("success", True):
                logger.error(f"Chyba při získání EPG: {response.get('errorMessage', 'Neznámá chyba')}")
                return None
                
            # Zpracování EPG dat
            epg_data = {}
            
            for item in response.get("items", []):
                item_channel_id = item.get("channel", {}).get("id")
                if not item_channel_id:
                    continue
                    
                # Vytvoření záznamu pro kanál
                if item_channel_id not in epg_data:
                    epg_data[item_channel_id] = []
                
                # Přidání programů
                for program in item.get("programs", []):
                    # Převod časových údajů z milisekund na sekundy
                    start_time = datetime.fromtimestamp(program["startTimeUTC"] / 1000)
                    end_time = datetime.fromtimestamp(program["endTimeUTC"] / 1000)
                    
                    prog_info = program.get("program", {})
                    prog_value = prog_info.get("programValue", {})
                    
                    epg_data[item_channel_id].append({
                        "schedule_id": program.get("scheduleId"),
                        "title": prog_info.get("title", ""),
                        "description": prog_info.get("description", ""),
                        "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "duration": int((end_time - start_time).total_seconds()),
                        "category": prog_info.get("programCategory", {}).get("desc", ""),
                        "year": prog_value.get("creationYear"),
                        "episode": prog_value.get("episodeId"),
                        "images": prog_info.get("images", [])
                    })
                    
            return epg_data
            
        except Exception as e:
            logger.error(f"Chyba při získání EPG: {e}")
            return None