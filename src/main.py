#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔═══════════════════════════════════════════════════════════════════╗
║  🎰 FLORIDA MORNING PREDICTOR v7.0 - FIXED PROGRESS              ║
║  ✅ Progreso fluido en tiempo real                                 ║
╚═══════════════════════════════════════════════════════════════════╝
"""

import flet as ft
import numpy as np
import json
from collections import Counter
from datetime import datetime
from typing import List, Dict
import warnings
import os
import time
import requests
import threading
import urllib3
import asyncio  
warnings.filterwarnings('ignore')
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# ============================================
# 🔧 CONFIGURACIÓN DE ESTADOS Y DRAWS
# ============================================

STATE_DRAW_CONFIG = {
    'FL': {'name': '🌴 Florida', 'draws': {'M': '☀️ Midday', 'E': '🌙 Evening'}},
    'GA': {'name': '🍑 Georgia', 'draws': {'M': '☀️ Midday', 'E': '🌙 Evening', 'N': '🌃 Night'}},
    'NY': {'name': '🗽 New York', 'draws': {'M': '☀️ Midday', 'E': '🌙 Evening'}}
}

DATA_JSON = "data.json"
EMAIL = "khloealba932@gmail.com"
PASSWORD = "Anabelyae04"

URLS_TXT = {
    ("GA", "M"): "https://www.lotterycorner.com/results/download/ga-cash-3-midday-2026.txt",
    ("GA", "E"): "https://www.lotterycorner.com/results/download/ga-cash-3-evening-2026.txt",
    ("GA", "N"): "https://www.lotterycorner.com/results/download/ga-cash-3-night-2026.txt",
    ("FL", "M"): "https://www.lotterycorner.com/results/download/fl-pick-3-midday-2026.txt",
    ("FL", "E"): "https://www.lotterycorner.com/results/download/fl-pick-3-evening-2026.txt",
    ("NY", "M"): "https://www.lotterycorner.com/results/download/ny-numbers-midday-2026.txt",
    ("NY", "E"): "https://www.lotterycorner.com/results/download/ny-numbers-evening-2026.txt",
}

PRIORIDAD = {
    "GA_M": 0, "FL_M": 1, "NY_M": 2,
    "GA_E": 3, "FL_E": 4, "NY_E": 5,
    "GA_N": 6
}


# ============================================
# 🎯 CLASE ANALIZADOR (Tu lógica original - SIN CAMBIOS)
# ============================================

class FloridaMorningAnalyzerV7:
    """Analizador Florida Morning - Lógica completa"""
    
    def __init__(self, json_file='data.json', state='FL', draw='M', solo_recientes=None):
        self.json_file = json_file
        self.state = state
        self.draw = draw
        self.solo_recientes = solo_recientes
        
        self.raw_data = []
        self.filtered_data = []
        self.all_fijos = []
        self.all_centenas = []
        self.all_decenas = []
        self.all_unidades = []
        self.all_fechas = []
        
        self.sequence_fijos = []
        self.sequence_centenas = []
        self.sequence_decenas = []
        self.sequence_unidades = []
        self.fechas = []
        
        self.analysis_results = {}
        self.prediction = {}
        
        self._load_and_process_data()
    
    def _load_and_process_data(self):
        """Cargar y filtrar datos"""
        print(f"\n📂 Cargando: {self.json_file}")
        
        with open(self.json_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if isinstance(content, str) and not content.strip().startswith('['):
            content = '[' + content + ']'
        self.raw_data = json.loads(content)
        
        print(f"   Total registros: {len(self.raw_data):,}")
        
        self.filtered_data = [
            r for r in self.raw_data 
            if r.get('state') == self.state and r.get('draw') == self.draw
        ]
        print(f"   Registros {self.state}-{self.draw}: {len(self.filtered_data):,}")
        
        for record in self.filtered_data:
            try:
                fecha = record.get('date', '')
                numbers_str = record.get('numbers', '')
                fijos = record.get('fijos', [])
                
                nums = numbers_str.split('-')
                if len(nums) >= 3:
                    centena, decena_num, unidad_num = int(nums[0]), int(nums[1]), int(nums[2])
                else:
                    continue
                
                fijo = int(fijos[0]) if len(fijos) >= 1 else int(f"{decena_num}{unidad_num}")
                
                if 0 <= fijo <= 99 and 0 <= centena <= 9:
                    self.all_fijos.append(fijo)
                    self.all_centenas.append(centena)
                    self.all_decenas.append(decena_num)
                    self.all_unidades.append(unidad_num)
                    self.all_fechas.append(fecha)
            except (ValueError, IndexError):
                continue
        
        if self.solo_recientes and self.solo_recientes < len(self.all_fijos):
            n = self.solo_recientes
            self.sequence_fijos = self.all_fijos[-n:]
            self.sequence_centenas = self.all_centenas[-n:]
            self.sequence_decenas = self.all_decenas[-n:]
            self.sequence_unidades = self.all_unidades[-n:]
            self.fechas = self.all_fechas[-n:]
        else:
            self.sequence_fijos = self.all_fijos[:]
            self.sequence_centenas = self.all_centenas[:]
            self.sequence_decenas = self.all_decenas[:]
            self.sequence_unidades = self.all_unidades[:]
            self.fechas = self.all_fechas[:]
        
        print(f"   ✅ Datos listos: {len(self.sequence_fijos)} sorteos")
    
    def run_complete_analysis(self) -> Dict:
        """Ejecutar análisis completo"""
        results = {
            'metadata': {
                'total_registros': len(self.sequence_fijos),
                'fecha_inicio': self.fechas[0] if self.fechas else '',
                'fecha_fin': self.fechas[-1] if self.fechas else '',
                'modo': 'RECIENTES' if self.solo_recientes else 'COMPLETO',
                'n_recientes': self.solo_recientes
            },
            'ultimos_fijos': self._get_ultimos_fijos(10),
            'analisis_centena': self._analizar_componente(self.sequence_centenas, 'CENTENA', 0, 9),
            'analisis_decena': self._analizar_componente(self.sequence_decenas, 'DECENA', 0, 9),
            'analisis_unidad': self._analizar_componente(self.sequence_unidades, 'UNIDAD', 0, 9),
            'frecuencia_fijos': self._analizar_frecuencia_fijos(),
            'analisis_cuadrantes': self._analizar_cuadrantes(),
            'patrones_recientes': self._analisis_patrones_recientes(),
            'tendencias': self._calcular_tendencias()
        }
        self.analysis_results = results
        return results
    
    def _analizar_componente(self, sequence, nombre, min_val, max_val) -> Dict:
        """✅ CORREGIDO: Ahora TODO ordenado por frecuencia"""
        total = len(sequence)
        freq = Counter(sequence)
        
        # Lista ordenada por frecuencia (descendente)
        calor_digital = [
            {'digito': d, 'veces': freq.get(d, 0), 
             'porcentaje': round((freq.get(d,0)/total)*100,2) if total > 0 else 0
            } for d in range(min_val, max_val+1)
        ]
        
        # ✅ ORDENAR POR VECES (descendente) - Esto era lo único que faltaba
        calor_digital.sort(key=lambda x: x['veces'], reverse=True)
        
        # ✅ CORREGIDO: Crear diccionario PERO manteniendo orden de frecuencia
        # Extraer solo los datos ordenados
        frecuencias_ordenadas = {
            item['digito']: {
                'count': item['veces'], 
                'percentage': item['porcentaje']
            }
            for item in calor_digital  # ← Ya viene ordenado por veces
        }
        
        return {
            'nombre': nombre, 
            'total_analizados': total,
            'frecuencias_detalle': frecuencias_ordenadas,  # ✅ Ahora SÍ ordenado
            'top_3_calientes': calor_digital[:3],
            'promedio': round(np.mean(sequence), 2) if sequence else 0
        }
    
    def _analizar_frecuencia_fijos(self) -> Dict:
        total = len(self.sequence_fijos)
        freq = Counter(self.sequence_fijos)
        top_10 = freq.most_common(10)
        ultima_aparicion = {}
        for i,fijo in enumerate(self.sequence_fijos):
            ultima_aparicion[fijo] = {'indice': i, 'fecha': self.fechas[i], 'dias_atras': len(self.sequence_fijos)-i}
        return {
            'total_fijos_unicos': len(freq),
            'top_10': [{'fijo': f, 'veces': c, 'porcentaje': round(c/total*100,1),
                      'ultima_fecha': ultima_aparicion[f]['fecha'], 'sorteos_atras': ultima_aparicion[f]['dias_atras']}
                     for f,c in top_10],
            'mas_repetido': top_10[0] if top_10 else {},
            'distribucion_completa': dict(freq)
        }
    
    def _analizar_cuadrantes(self) -> Dict:
        cuadrantes = {1: {'rango':'00-24','count':0}, 2: {'rango':'25-49','count':0},
                     3: {'rango':'50-74','count':0}, 4: {'rango':'75-99','count':0}}
        for fijo in self.sequence_fijos:
            if 0<=fijo<=24: cuadrantes[1]['count']+=1
            elif 25<=fijo<=49: cuadrantes[2]['count']+=1
            elif 50<=fijo<=74: cuadrantes[3]['count']+=1
            else: cuadrantes[4]['count']+=1
        total = len(self.sequence_fijos)
        for q in cuadrantes: cuadrantes[q]['porcentaje'] = round((cuadrantes[q]['count']/total)*100,1) if total>0 else 0
        cuad_dom = max(cuadrantes.items(), key=lambda x: x[1]['count'])
        return {'detalle_por_cuadrante': cuadrantes,
                'cuadrante_dominante': {'numero': cuad_dom[0], 'rango': cuad_dom[1]['rango'],
                                      'count': cuad_dom[1]['count'], 'porcentaje': cuad_dom[1]['porcentaje']}}
    
    def _get_ultimos_fijos(self, n=10) -> List[Dict]:
        ultimos = []
        total = len(self.sequence_fijos)
        for i in range(max(0,total-n), total):
            ultimos.append({'fecha': self.fechas[i], 'fijo': self.sequence_fijos[i],
                         'centena': self.sequence_centenas[i], 'decena': self.sequence_decenas[i],
                         'unidad': self.sequence_unidades[i], 'cuadrante': self._get_cuadrante(self.sequence_fijos[i]),
                         'posicion_desde_fin': total-i, 'es_ultimo': i==total-1})
        return ultimos
    
    def _analisis_patrones_recientes(self) -> Dict:
        return {'ultimos_10_decenas': self.sequence_decenas[-10:],
                'ultimos_10_unidades': self.sequence_unidades[-10:],
                'decena_mas_freq': Counter(self.sequence_decenas[-10:]).most_common(3),
                'unidad_mas_freq': Counter(self.sequence_unidades[-10:]).most_common(3)}
    
    def _calcular_tendencias(self) -> Dict:
        if len(self.sequence_fijos)<5: return {}
        diffs = np.diff(self.sequence_fijos[-30:])
        subidas = sum(1 for d in diffs if d>0)
        bajadas = sum(1 for d in diffs if d<0)
        total = len(diffs)
        return {'direccion_dominante': 'SUBIENDO' if subidas>bajadas else ('BAJANDO' if bajadas>subidas else 'ESTABLE'),
                'ultimo_movimiento': 'SUBIÓ' if diffs[-1]>0 else ('BAJÓ' if diffs[-1]<0 else 'IGUAL'),
                'magnitud_ultimo': int(diffs[-1]) if len(diffs)>0 else 0,
                'porcentaje_subidas': round(subidas/total*100,1), 'porcentaje_bajadas': round(bajadas/total*100,1)}
    
    def _get_cuadrante(self, numero):
        if 0<=numero<=24: return 1
        elif 25<=numero<=49: return 2
        elif 50<=numero<=74: return 3
        else: return 4
    
    def generate_prediction(self) -> Dict:
        if not self.analysis_results: self.run_complete_analysis()
        analysis = self.analysis_results
        dec = analysis['analisis_decena']
        uni = analysis['analisis_unidad']
        cen = analysis['analisis_centena']
        
        top_decenas = [x['digito'] for x in dec['top_3_calientes']]
        top_unidades = [x['digito'] for x in uni['top_3_calientes']]
        top_centenas = [x['digito'] for x in cen['top_3_calientes']]
        cuadrante_dom = analysis['analisis_cuadrantes']['cuadrante_dominante']['numero']
        
        candidatos = []; vistos = set()
        for c in top_centenas[:2]:
            for d in top_decenas[:3]:
                for u in top_unidades[:3]:
                    fijo = d*10+u
                    if 0<=fijo<=99 and fijo not in vistos:
                        vistos.add(fijo); score=0
                        if d in top_decenas: score+=(4-top_decenas.index(d))*20
                        if u in top_unidades: score+=(4-top_unidades.index(u))*18
                        if self._get_cuadrante(fijo)==cuadrante_dom: score+=25
                        freq_fijos = analysis['frecuencia_fijos']['distribucion_completa']
                        if fijo in freq_fijos and freq_fijos[fijo]>=2: score+=min(freq_fijos[fijo]*2,15)
                        ult = [f['fijo'] for f in analysis['ultimos_fijos'][:3]]
                        if fijo in ult: score-=20
                        candidatos.append({'fijo':fijo,'centena':c,'decena':d,'unidad':u,
                                       'cuadrante':self._get_cuadrante(fijo),'puntuacion':score})
        
        candidatos.sort(key=lambda x:x['puntuacion'], reverse=True)
        top_10 = candidatos[:10]
        if top_10:
            max_score = top_10[0]['puntuacion']
            for i,pred in enumerate(top_10):
                pred['confianza'] = round(45+(pred['puntuacion']/max_score)*35,1) if max_score>0 else 50
                pred['ranking'] = i+1
        
        principal = top_10[0] if top_10 else {'fijo':50,'decena':5,'unidad':0}
        estrategia_serie = self._calcular_estrategia_serie(principal, cuadrante_dom)
        
        prediction = {
            'principal': principal, 'alternativas': top_10[1:6],
            'componentes_recomendados': {'centena':top_centenas[0], 'decena_principal':top_decenas[0],
                                        'decena_alternativas':top_decenas[:3],
                                        'unidad_principal':top_unidades[0], 'unidad_alternativas':top_unidades[:3]},
            'cuadrante_recomendado': cuadrante_dom, 'confianza_global': principal.get('confianza',60),
            'justificacion': self._generar_justificacion(principal,analysis),
            'estrategias': self._generar_estrategias(principal,top_10[:5],cuadrante_dom),
            'estrategia_serie': estrategia_serie
        }
        self.prediction = prediction
        return prediction
    
    def _calcular_estrategia_serie(self, principal, cuadrante_dom):
        fijo, decena = principal['fijo'], principal['decena']
        serie_inicio, serie_fin = decena*10, decena*10+9
        serie_completa = list(range(serie_inicio, serie_fin+1))
        cuad_ranges = {1:(0,24), 2:(25,49), 3:(50,74), 4:(75,99)}
        cuad_start, cuad_end = cuad_ranges[cuadrante_dom]
        todos_dentro = all(cuad_start<=n<=cuad_end for n in serie_completa)
        
        resultado = {'recomendar':False, 'decena':decena, 'serie':serie_completa,
                  'serie_str':f"{serie_inicio:02d}-{serie_fin:02d}",
                  'cuadrante_objetivo':cuadrante_dom, 'esta_dentro':todos_dentro, 'razon':''}
        
        if todos_dentro:
            resultado['recomendar'] = True
            resultado['razon'] = f"✅ Decena {decena} DENTRO Q{cuadrante_dom} → SERIE COMPLETA"
        else:
            solapamiento = [n for n in serie_completa if cuad_start<=n<=cuad_end]
            if len(solapamiento)>=5:
                resultado['recomendar'] = True; resultado['serie_parcial'] = solapamiento
                resultado['razon'] = f"⚠️ Parcial: {len(solapamiento)}/10"
            else:
                resultado['razon'] = f"❌ Fuera del cuadrante"
        return resultado
    
    def _generar_justificacion(self, principal, analysis):
        justificaciones = []
        d,u,f = principal['decena'], principal['unidad'], principal['fijo']
        dec_info = analysis['analisis_decena']['frecuencias_detalle'].get(d,{})
        uni_info = analysis['analisis_unidad']['frecuencias_detalle'].get(u,{})
        if dec_info.get('percentage',0)>12: justificaciones.append(f"✅ Decena {d}: {dec_info['percentage']}%")
        if uni_info.get('percentage',0)>10: justificaciones.append(f"✅ Unidad {u}: {uni_info['percentage']}%")
        cuad_dom = analysis['analisis_cuadrantes']['cuadrante_dominante']
        if principal['cuadrante']==cuad_dom['numero']: justificaciones.append(f"✅ Cuadrante {cuad_dom['numero']}: {cuad_dom['porcentaje']}%")
        freq_fijos = analysis['frecuencia_fijos']['distribucion_completa']
        if f in freq_fijos and freq_fijos[f]>=2: justificaciones.append(f"✅ Fijo {f:02d}: {freq_fijos[f]} veces")
        tend = analysis.get('tendencias',{})
        justificaciones.append(f"📈 Tendencia: {tend.get('direccion_dominante','Estable')}")
        return justificaciones
    
    def _generar_estrategias(self, principal, alternatives, cuadrante):
        return {
            'conservadora': {'nombre':'CONSERVADORA (~25%)', 'descripcion':f'Q{cuadrante}',
                            'rango':{1:'00-24',2:'25-49',3:'50-74',4:'75-99'}[cuadrante], 'riesgo':'BAJO'},
            'balanceada': {'nombre':'BALANCEADA (5 números)', 'descripcion':f"{principal['fijo']:02d} + 4 alt",
                          'numeros':[principal['fijo']]+[a['fijo'] for a in alternatives[:4]], 'riesgo':'MEDIO'},
            'agresiva': {'nombre':'AGRESIVA (1 número)', 'descripcion':f"{principal['fijo']:02d}",
                        'completo':f"{principal['centena']}-{principal['decena']}-{principal['unidad']}", 'riesgo':'ALTO'}
        }


# ============================================
# 🎨 INTERFAZ FLET 0.84.0 - CON PROGRESO FIJO
# ============================================

class FloridaPredictorApp:
    """Interfaz Gráfica - Con Actualización de BD Fluida CORREGIDA"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.analyzer = None
        
        # Configurar página (EXACTO igual que tu original)
        self.page.title = "🎰 Predictor v7.0"
        self.page.vertical_alignment = ft.MainAxisAlignment.START
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.page.scroll = ft.ScrollMode.AUTO
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.padding = 10
        
        # Controles principales
        self.dd_state = None
        self.dd_draw = None
        self.input_recientes = None
        self.contenedor_resultados = None
        
        # Componentes de actualización de BD
        self.dialog_update = None
        self.progress_bar = None
        self.progress_text = None
        self.log_list_view = None
        self.status_icon = None
        self.status_text = None
        
        self.configurar_ui()
    
    def configurar_ui(self):
        """Configurar UI - EXACTA igual que tu original"""
        
        # AppBar (AGREGADO icono de update)
        self.page.appbar = ft.AppBar(
            title=ft.Text("🎰 Predictor v7.0", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            center_title=True,
            bgcolor=ft.Colors.BLUE_800,
            actions=[
                ft.IconButton(ft.Icons.UPDATE, on_click=self.iniciar_actualizacion, 
                            tooltip="Actualizar Base de Datos", icon_color=ft.Colors.AMBER_300),
                ft.IconButton(ft.Icons.INFO, on_click=self.mostrar_ayuda, icon_color=ft.Colors.WHITE)
            ]
        )
        
        # Dropdown Estado
        self.dd_state = ft.Dropdown(
            label="Estado (State)",
            width=400,
            options=[
                ft.dropdown.Option("FL", "🌴 Florida"),
                ft.dropdown.Option("GA", "🍑 Georgia"),
                ft.dropdown.Option("NY", "🗽 New York")
            ],
            value="FL",
            on_select=self.cambiar_estado
        )
        
        # Dropdown Draw
        self.dd_draw = ft.Dropdown(
            label="Sorteo (Draw)",
            width=400,
            value="M"
        )
        self.actualizar_opciones_draw("FL")
        
        # Input N recientes
        self.input_recientes = ft.TextField(
            label="Últimos N Sorteos",
            width=200,
            value="112",
            keyboard_type=ft.KeyboardType.NUMBER
        )
        
        # Contenedor de resultados
        self.contenedor_resultados = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.START
        )
        
        # === DIÁLOGO DE ACTUALIZACIÓN ===
        self.log_list_view = ft.ListView(expand=True, height=180, spacing=2, auto_scroll=True, padding=10)
        self.progress_bar = ft.ProgressBar(width=float('inf'), height=8, border_radius=4, color=ft.Colors.BLUE_400, bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.GREY_500))
        self.progress_text = ft.Text("Preparando...", size=12, color=ft.Colors.GREY_400, text_align=ft.TextAlign.CENTER)
        self.status_icon = ft.Icon(ft.Icons.SYNC, size=32, color=ft.Colors.BLUE_400)
        self.status_text = ft.Text("Estado: Listo", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_400)
        
        self.dialog_update = ft.AlertDialog(
            modal=True,
            title=ft.Row(controls=[
                self.status_icon,
                ft.Column(controls=[
                    ft.Text("Actualizando Base de Datos", size=16, weight=ft.FontWeight.BOLD),
                    self.status_text
                ], expand=True, horizontal_alignment=ft.CrossAxisAlignment.START)
            ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            content=ft.Container(
                content=ft.Column(controls=[
                    ft.Column(controls=[self.progress_text, self.progress_bar], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                    ft.Divider(height=1),
                    ft.Row(controls=[ft.Icon(ft.Icons.TERMINAL, size=16, color=ft.Colors.CYAN_300), ft.Text("Registro de actividad:", size=12, weight=ft.FontWeight.W_600, color=ft.Colors.CYAN_300)], spacing=8),
                    ft.Container(content=self.log_list_view, border=ft.border.all(1, ft.Colors.with_opacity(0.3, ft.Colors.GREY_700)), border_radius=ft.border_radius.all(8), bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.GREY_900))
                ], tight=False, spacing=10),
                width=550
            ),
            actions=[ft.TextButton("Cerrar", on_click=lambda _: self.cerrar_dialogo_actualizacion(), style=ft.ButtonStyle(color=ft.Colors.BLUE_300))],
            actions_alignment=ft.MainAxisAlignment.END
        )
        
        # Layout EXACTO igual que tu original + botón Actualizar DB
        self.page.add(
            ft.SafeArea(
                ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            padding=10,
                            bgcolor=ft.Colors.GREY_900,
                            border_radius=10,
                            shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.GREY_300),
                            width=600,
                            content=ft.Column(controls=[
                                ft.Text("⚙️ Configuración de Análisis", size=16, weight=ft.FontWeight.BOLD),
                                ft.Column(
                                    controls=[self.dd_state, self.dd_draw, self.input_recientes],
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    spacing=10
                                ),
                                ft.Row(
                                    scroll="auto", expand=True,
                                    controls=[
                                        ft.Button("🎯 Analizar", on_click=self.ejecutar_analisis, expand=True,
                                               style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_600, color=ft.Colors.WHITE)),
                                        ft.Container(width=10),
                                        ft.Button("📊 Ver Todo", on_click=self.mostrar_todo, expand=True,
                                               style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN_600, color=ft.Colors.WHITE)),
                                        # === BOTÓN ACTUALIZAR DB ===
                                        ft.Container(width=10),
                                        ft.Button("Actualizar DB", icon=ft.Icons.REFRESH, on_click=self.iniciar_actualizacion, expand=True,
                                               style=ft.ButtonStyle(bgcolor=ft.Colors.ORANGE_600, color=ft.Colors.WHITE))
                                    ]
                                )
                            ])
                        ),
                        
                        ft.Container(height=10),
                        
                        ft.Container(
                            padding=5,
                            bgcolor=ft.Colors.GREY_900,
                            border_radius=5,
                            content=self.contenedor_resultados
                        )
                    ]
                )
            )
        )
    
    # ================================================
    # ✅ MÉTODOS DE ACTUALIZACIÓN - CORREGIDOS PARA PROGRESO EN TIEMPO REAL
    # ================================================
    
    def cerrar_dialogo_actualizacion(self):
        """Cerrar diálogo de actualización"""
        self.dialog_update.open = False
        self.progress_bar.value = 0
        self.page.update()
    
    def log_fluido(self, mensaje, tipo="info"):
        """
        ✅ CORREGIDO: Log con actualización forzada inmediata
        """
        colores = {"info": ft.Colors.BLUE_200, "success": ft.Colors.GREEN_300, "error": ft.Colors.RED_300, "warning": ft.Colors.AMBER_300}
        iconos = {"info": ft.Icons.INFO, "success": ft.Icons.CHECK_CIRCLE, "error": ft.Icons.ERROR, "warning": ft.Icons.WARNING}
        color = colores.get(tipo, ft.Colors.BLUE_200)
        icono = iconos.get(tipo, ft.Icons.INFO)
        
        log_entry = ft.Container(
            content=ft.Row(controls=[ft.Icon(icono, size=16, color=color), ft.Text(mensaje, size=12, color=color, weight=ft.FontWeight.W_500)], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.Padding(left=10, right=10, top=4, bottom=4)
        )
        self.log_list_view.controls.append(log_entry)
        
        # ✅ FORZAR ACTUALIZACIÓN INMEDIATA
        self.log_list_view.update()
        self.page.update()
    
    def actualizar_progreso_fluido(self, valor, texto=None):
        """
        ✅ CORREGIDO: Progreso con actualización forzada inmediata
        """
        self.progress_bar.value = valor
        if texto: 
            self.progress_text.value = texto
        
        # Cambiar color según progreso
        if valor < 0.3: 
            self.progress_bar.color = ft.Colors.ORANGE_400
        elif valor < 0.7: 
            self.progress_bar.color = ft.Colors.BLUE_400
        else: 
            self.progress_bar.color = ft.Colors.GREEN_400
        
        # ✅ FORZAR ACTUALIZACIÓN INMEDIATA DE CADA COMPONENTE
        self.progress_bar.update()
        if texto: self.progress_text.update()
        self.page.update()
    
    def cambiar_estado_actualizacion(self, estado, mensaje):
        """
        ✅ CORREGIDO: Estado con actualización forzada inmediata
        """
        estados_config = {
            "conectando": {"icono": ft.Icons.SYNC, "color": ft.Colors.BLUE_400},
            "descargando": {"icono": ft.Icons.DOWNLOAD, "color": ft.Colors.ORANGE_400},
            "procesando": {"icono": ft.Icons.SETTINGS, "color": ft.Colors.PURPLE_400},
            "exitoso": {"icono": ft.Icons.CHECK_CIRCLE, "color": ft.Colors.GREEN_400},
            "error": {"icono": ft.Icons.ERROR, "color": ft.Colors.RED_400}
        }
        config = estados_config.get(estado, estados_config["conectando"])
        
        self.status_icon.icon = config["icono"]
        self.status_icon.color = config["color"]
        self.status_text.value = mensaje
        self.status_text.color = config["color"]
        
        # ✅ FORZAR ACTUALIZACIÓN INMEDIATA
        self.status_icon.update()
        self.status_text.update()
        self.page.update()
    
    def iniciar_actualizacion(self, e):
        """Iniciar actualización de BD"""
        # Resetear componentes
        self.log_list_view.controls.clear()
        self.progress_bar.value = 0
        self.progress_text.value = "Preparando..."
        
        # Mostrar diálogo
        self.page.show_dialog(self.dialog_update)
        self.page.update()
        
        # Estado inicial
        self.cambiar_estado_actualizacion("conectando", "🔐 Conectando al servidor...")
        self.log_fluido("🚀 Iniciando proceso de actualización...", "info")
        self.actualizar_progreso_fluido(0.05, "Inicializando...")
        
        self.page.run_task(self.logica_actualizar_db_fluida)
    
    async def logica_actualizar_db_fluida(self):  # ← agrega "async"
        """Lógica de actualización - AHORA SÍ FUNCIONA EN TIEMPO REAL"""
        try:
            # === FASE 1 ===
            self.log_fluido("🔐 Conectando...", "info")
            self.actualizar_progreso_fluido(0.1, "Conectando...")
            
            await asyncio.sleep(0.3)  # ← cambia time.sleep por await asyncio.sleep
            
            session = requests.Session()
            session.headers.update({"User-Agent": "Mozilla/5.0..."})
            
            self.log_fluido("📡 Enviando credenciales...", "info")
            
            try:
                r = session.post("https://www.lotterycorner.com/insider/login", 
                               data={"email": EMAIL, "pwd": PASSWORD}, timeout=20)
            except Exception as ex:
                raise Exception(f"❌ Error conexión: {ex}")
            
            if "Logout" not in r.text:
                raise Exception("❌ Login fallido")
            
            self.cambiar_estado_actualizacion("exitoso", "✅ Conectado")
            self.log_fluido("✅ ¡Login OK!", "success")
            self.actualizar_progreso_fluido(0.15, "Conectado ✓")
            
            await asyncio.sleep(0.8)  # ← pausa visible
            
            # === FASE 2: DESCARGA ===
            self.cambiar_estado_actualizacion("descargando", "⬇️ Descargando...")
            self.actualizar_progreso_fluido(0.2, "Descargando...")
            
            contenidos = {}
            pasos = len(URLS_TXT)
            
            for i, ((estado, sorteo), url) in enumerate(URLS_TXT.items(), 1):
                prog = 0.2 + (i / pasos) * 0.6
                
                self.log_fluido(f"⬇️ [{i}/{pasos}] {estado}_{sorteo}...", "info")
                self.actualizar_progreso_fluido(prog, f"Descargando {estado}_{sorteo} ({i}/{pasos})...")
                
                await asyncio.sleep(0.15)  # ← pausa para ver el log
                
                try:
                    r = session.get(url, timeout=30)
                    r.raise_for_status()
                    contenidos[(estado, sorteo)] = r.text
                    self.log_fluido(f"   ✅ {len(r.text)/1024:.1f} KB", "success")
                    await asyncio.sleep(0.2)  # ← pausa para ver el ✓ verde
                except Exception as ex:
                    self.log_fluido(f"   ❌ Error: {str(ex)[:40]}", "error")
                    await asyncio.sleep(0.1)
            
            self.actualizar_progreso_fluido(0.8, "Procesando...")
            self.cambiar_estado_actualizacion("procesando", "⚙️ Procesando...")
            self.log_fluido("🔨 Guardando datos...", "info")
            
            await asyncio.sleep(0.5)
            
            # === FASE 3: GUARDAR ===
            combinaciones = {}
            if os.path.exists(DATA_JSON):
                with open(DATA_JSON, "r") as f:
                    for s in json.load(f):
                        combinaciones[f"{s['date']}-{s['state']}-{s['draw']}"] = s
            
            nuevos = 0
            for (est, sort), texto in contenidos.items():
                for s in self.parsear_txt(texto, est, sort):
                    clave = f"{s['date']}-{s['state']}-{s['draw']}"
                    if clave not in combinaciones:
                        combinaciones[clave] = s
                        nuevos += 1
            
            todos = sorted(combinaciones.values(), 
                          key=lambda s: (datetime.strptime(s["date"], "%d/%m/%y"), 
                                        PRIORIDAD.get(f'{s["state"]}_{s["draw"]}', 99)))
            
            with open(DATA_JSON, "w") as f:
                json.dump(todos, f, indent=2)
            
            self.log_fluido(f"💾 Guardado: {DATA_JSON}", "success")
            self.actualizar_progreso_fluido(0.95, "Finalizando...")
            await asyncio.sleep(0.5)
            
            # === FASE 4: LISTO ===
            self.cambiar_estado_actualizacion("exitoso", "¡Completado!")
            self.actualizar_progreso_fluido(1.0, "✅ Listo")
            
            self.log_fluido("═" * 35, "info")
            await asyncio.sleep(0.1)
            self.log_fluido("🎉 ¡PROCESO TERMINADO!", "success")
            await asyncio.sleep(0.15)
            self.log_fluido(f"📊 Total: {len(todos):,} registros", "success")
            await asyncio.sleep(0.1)
            self.log_fluido(f"➕ Nuevos: {nuevos:,}", "success")
            self.log_fluido(f"🕐 {datetime.now().strftime('%H:%M:%S')}", "info")
            
            self.notificar(f"✅ BD actualizada: {len(todos)} registros", ft.Colors.GREEN_500)
            
        except Exception as e:
            self.cambiar_estado_actualizacion("error", "❌ Error")
            self.actualizar_progreso_fluido(0, "Error")
            self.log_fluido(f"❌ ERROR: {str(e)}", "error")
            self.notificar(f"❌ {str(e)}", ft.Colors.RED_500)
    
    def parsear_txt(self, texto, estado, sorteo):
        """Parsear archivo TXT de lotería"""
        resultados = []
        lineas = texto.strip().splitlines()[1:]
        for linea in lineas:
            partes = linea.split(",")
            if len(partes) >= 2:
                fecha_str, numeros = partes[0].strip(), partes[1].strip()
                try:
                    fecha = datetime.strptime(fecha_str, "%a %m/%d/%Y")
                except ValueError: continue
                if estado == "FL":
                    digitos = numeros.split("-")
                    if len(digitos) >= 3: numeros = "-".join(digitos[:3])
                fecha_fmt = fecha.strftime("%d/%m/%y")
                nums_parts = numeros.split("-")
                if len(nums_parts) >= 3:
                    f1 = nums_parts[1] + nums_parts[2]
                    f2 = nums_parts[2] + nums_parts[1]
                    resultados.append({"date": fecha_fmt, "state": estado, "draw": sorteo, "numbers": numeros, "fijos": [f1, f2]})
        return resultados
    
    # ================================================
    # === MÉTODOS ORIGINALES (SIN CAMBIOS) ===
    # ================================================
    
    def cambiar_estado(self, e):
        """Actualizar opciones de Draw cuando cambia Estado"""
        estado = e.control.value
        self.actualizar_opciones_draw(estado)
        self.page.update()
    
    def actualizar_opciones_draw(self, estado):
        """Actualizar dropdown de draws según estado"""
        draws = STATE_DRAW_CONFIG[estado]['draws']
        self.dd_draw.options = [ft.dropdown.Option(k, v) for k,v in draws.items()]
        self.dd_draw.value = list(draws.keys())[0]
    
    def mostrar_ayuda(self, e):
        """Mostrar diálogo de ayuda"""
        dialog = ft.AlertDialog(
            title=ft.Text("Ayuda"),
            content=ft.Column([
                ft.Text("🎰 Florida Morning Predictor v7.0", size=16, weight=ft.FontWeight.BOLD),
                ft.Text(""),
                ft.Text("1. Selecciona Estado (FL/GA/NY)"),
                ft.Text("2. Selecciona Sorteo (M/E/N)"),
                ft.Text("3. Ingresa N de sorteos recientes"),
                ft.Text("4. Presiona 'Analizar'"),
                ft.Text(""),
                ft.Text("✨ Características:", weight=ft.FontWeight.BOLD),
                ft.Text("• Análisis Centena/Decena/Unidad"),
                ft.Text("• Top 10 Fijos frecuentes"),
                ft.Text("• Análisis de Cuadrantes"),
                ft.Text("• Estrategia de Serie de Decena"),
                ft.Text("• Predicción con Confianza %"),
                ft.Text("• Actualización de BD en tiempo real")
            ], scroll="auto", expand=True),
            actions=[ft.TextButton("Cerrar", on_click=lambda _: self.cerrar_dialogo(dialog))]
        )
        self.page.show_dialog(dialog)
    
    def cerrar_dialogo(self, dialog):
        dialog.open = False
        self.page.update()
    
    def notificar(self, mensaje, color=None):
        """Mostrar notificación SnackBar"""
        self.page.show_dialog(ft.SnackBar(ft.Text(mensaje), bgcolor=color or ft.Colors.BLUE_500))
    
    def ejecutar_analisis(self, e):
        """Ejecutar análisis"""
        state = self.dd_state.value
        draw = self.dd_draw.value
        
        try:
            recientes = int(self.input_recientes.value) if self.input_recientes.value else None
        except ValueError:
            self.notificar("❌ Ingrese número válido", ft.Colors.RED_500)
            return
        
        self.contenedor_resultados.controls.clear()
        self.contenedor_resultados.controls.append(ft.ProgressRing(width=50, height=50, stroke_width=5))
        self.contenedor_resultados.controls.append(
            ft.Text(f"⏳ Analizando {state}-{draw} con últimos {recientes or 'TODOS'} sorteos...", size=14, color=ft.Colors.GREY_500)
        )
        self.page.update()
        
        self.page.run_thread(self.logica_analisis, state, draw, recientes)
    
    def logica_analisis(self, state, draw, recientes):
        """Lógica de análisis en thread separado"""
        try:
            self.analyzer = FloridaMorningAnalyzerV7(
                json_file='data.json',
                state=state,
                draw=draw,
                solo_recientes=recientes
            )
            
            results = self.analyzer.run_complete_analysis()
            prediction = self.analyzer.generate_prediction()
            
            self.mostrar_resultados(results, prediction)
            
        except Exception as ex:
            self.contenedor_resultados.controls.clear()
            self.contenedor_resultados.controls.append(
                ft.Text(f"❌ Error: {str(ex)}", size=14, color=ft.Colors.RED_500)
            )
            self.page.update()
    
    # === LOS MÉTODOS DE VISUALIZACIÓN SIGUEN IGUALES (mostrar_resultados, crear_stat_box, etc.) ===
    # [Aquí irían todos tus métodos originales sin cambios...]
    
    def mostrar_resultados(self, results, prediction):
        """Mostrar todos los resultados - TU CÓDIGO ORIGINAL"""
        self.contenedor_resultados.controls.clear()
        
        pp = prediction['principal']
        serie = prediction['estrategia_serie']
        meta = results['metadata']
        # === NUEVO: TARJETA DE PERÍODO (AL INICIO) ===
        self.contenedor_resultados.controls.append(
            ft.Container(
                padding=15,
                bgcolor=ft.Colors.with_opacity(0.08, ft.Colors.CYAN),
                border_radius=12,
                border=ft.border.all(1, ft.Colors.CYAN_300),
                content=ft.Row(controls=[
                    ft.Icon(ft.Icons.CALENDAR_TODAY, size=24, color=ft.Colors.CYAN_300),
                    ft.Column(controls=[
                        ft.Text(f"📅 PERÍODO DE ANÁLISIS", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN_300),
                        ft.Text(f"Desde: {meta.get('fecha_inicio', 'N/A')}  →  Hasta: {meta.get('fecha_fin', 'N/A')}", 
                              size=12, color=ft.Colors.WHITE),
                        ft.Text(f"Modo: {meta.get('modo', 'N/A')} | Registros: {meta.get('total_registros', 0):,}", 
                              size=11, color=ft.Colors.GREY_400)
                    ], expand=True, horizontal_alignment=ft.CrossAxisAlignment.START)
                ], spacing=12)
            )
        )
        
        self.contenedor_resultados.controls.append(ft.Container(height=10))
            
        self.contenedor_resultados.controls.append(
            ft.Container(
                padding=20,
                bgcolor=ft.Colors.BLUE_800,
                border_radius=15,
                width=float('inf'),
                content=ft.Column(controls=[
                    ft.Row(controls=[
                        ft.Icon(ft.Icons.STARS, size=60, color=ft.Colors.AMBER),
                        ft.Column(controls=[
                            ft.Text("FIJO PREDICHO", size=12, color=ft.Colors.AMBER_100),
                            ft.Text(f"{pp['fijo']:02d}", size=72, weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN_300)
                        ])
                    ], alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    
                    ft.Divider(height=2),
                    
                    ft.Row(controls=[
                        self.crear_stat_box("CENTENA", str(pp['centena']), ft.Colors.PURPLE_300),
                        self.crear_stat_box("DECENA", str(pp['decena']), ft.Colors.BLUE_300),
                        self.crear_stat_box("UNIDAD", str(pp['unidad']), ft.Colors.GREEN_300),
                        self.crear_stat_box("CUADRANTE", f"Q{pp['cuadrante']}", ft.Colors.ORANGE_300),
                    ], alignment=ft.MainAxisAlignment.CENTER, spacing=15),
                    
                    ft.Divider(height=2),
                    
                    ft.Column(controls=[
                        ft.Text(f"CONFIANZA: {prediction['confianza_global']}%", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        ft.ProgressBar(value=prediction['confianza_global']/100, color=ft.Colors.GREEN_400, height=15)
                    ], horizontal_alignment=ft.MainAxisAlignment.CENTER),
                    
                    *([ft.Container(
                            content=ft.Row(controls=[
                                ft.Icon(ft.Icons.LOCAL_FIRE_DEPARTMENT, color=ft.Colors.RED_400),
                                ft.Text(f"🔥 SERIE ACTIVA: Decena {serie['decena']} ({serie['serie_str']})", 
                                       weight=ft.FontWeight.BOLD, color=ft.Colors.RED_300)
                            ]),
                            padding=10,
                            bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.RED),
                            border_radius=10
                        )] if serie['recomendar'] else []),
                ], horizontal_alignment=ft.MainAxisAlignment.CENTER)
            )
        )
        
        self.contenedor_resultados.controls.append(ft.Container(height=15))
        self.contenedor_resultados.controls.append(
            ft.Text("🔄 ALTERNATIVAS RECOMENDADAS", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER_300)
        )
        self.contenedor_resultados.controls.append(
            ft.Row(controls=[
                self.crear_alt_card(alt, i) for i,alt in enumerate(prediction['alternativas'][:5])
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=10, wrap=True)
        )
        
        self.contenedor_resultados.controls.append(ft.Container(height=15))
        self.contenedor_resultados.controls.append(
            ft.Container(
                padding=15,
                bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE24),
                border_radius=10,
                content=ft.Column(controls=[
                    ft.Text("📝 JUSTIFICACIÓN", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN_300),
                    *[ft.Container(
                        content=ft.Text(j, size=13, color=ft.Colors.GREEN_200),
                        padding=ft.Padding.symmetric(horizontal=15, vertical=8),
                        bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.GREEN),
                        border_radius=ft.border_radius.all(8)
                    ) for j in prediction['justificacion']]
                ])
            )
        )
        
        self.contenedor_resultados.controls.append(ft.Container(height=20))
        self.contenedor_resultados.controls.append(
            ft.Text("🔢 ANÁLISIS DE COMPONENTES", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN_300)
        )
        
        for titulo, data, color in [
            ("1️⃣ CENTENA", results['analisis_centena'], ft.Colors.PURPLE),
            ("2️⃣ DECENA", results['analisis_decena'], ft.Colors.BLUE),
            ("3️⃣ UNIDAD", results['analisis_unidad'], ft.Colors.GREEN)
        ]:
            self.contenedor_resultados.controls.append(self.crear_tarjeta_componente(titulo, data, color))

        self.contenedor_resultados.controls.append(ft.Container(height=15))
        self.contenedor_resultados.controls.append(
            ft.Text("🏆 TOP 10 FIJOS MÁS FRECUENTES", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER_300)
        )
        self.contenedor_resultados.controls.append(self.crear_tarjeta_top10_fijos(results['frecuencia_fijos']))
            
        self.contenedor_resultados.controls.append(ft.Container(height=20))
        self.contenedor_resultados.controls.append(self.crear_tarjeta_cuadrantes(results['analisis_cuadrantes']))
        
        self.contenedor_resultados.controls.append(ft.Container(height=20))
        self.contenedor_resultados.controls.append(self.crear_tarjeta_tendencias(results['tendencias'], results['patrones_recientes']))
        
        self.contenedor_resultados.controls.append(ft.Container(height=20))
        self.contenedor_resultados.controls.append(self.crear_tarjeta_serie(prediction['estrategia_serie'], prediction['principal']))
        
        self.contenedor_resultados.controls.append(ft.Container(height=20))
        self.contenedor_resultados.controls.append(self.crear_tarjeta_resumen(results['metadata'], prediction))
        
        self.contenedor_resultados.controls.append(ft.Container(height=15))
        self.contenedor_resultados.controls.append(
            ft.Container(
                content=ft.Row(controls=[
                    ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color=ft.Colors.AMBER),
                    ft.Text("⚠️ Las loterías son juegos de azar. Juegue responsablemente.", color=ft.Colors.AMBER, italic=True)
                ]),
                padding=15,
                bgcolor=ft.Colors.with_opacity(0.08, ft.Colors.AMBER),
                border_radius=10
            )
        )
        
        self.page.update()
        self.notificar("✅ ¡Análisis completado!", ft.Colors.GREEN_500)
    
    def crear_stat_box(self, titulo, valor, color):
        return ft.Container(
            content=ft.Column(controls=[
                ft.Text(titulo, size=10, color=ft.Colors.GREY_500),
                ft.Text(valor, size=15, weight=ft.FontWeight.BOLD, color=color)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            width=110,
            padding=10,
            bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE24),
            border_radius=ft.border_radius.all(10)
        )
    
    def crear_alt_card(self, alt, idx):
        emojis = ['🥇', '🥈', '🥉', '4️⃣', '5️⃣']
        return ft.Container(
            content=ft.Column(controls=[
                ft.Text(emojis[idx] if idx<len(emojis) else str(idx+1), size=24),
                ft.Text(f"{alt['fijo']:02d}", size=32, weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN_200),
                ft.Text(f"#{alt['ranking']} | {alt['confianza']:.1f}%", size=11, color=ft.Colors.GREY_400)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            width=120,
            padding=15,
            bgcolor=ft.Colors.with_opacity(0.08, ft.Colors.WHITE24),
            border_radius=ft.border_radius.all(15),
            alignment=ft.Alignment.CENTER
        )
    
    def crear_tarjeta_componente(self, titulo, data, color_base):
        emojis = ['🥇', '🥈', '🥉']
        top_items = [
            ft.Container(
                content=ft.Row(controls=[
                    ft.Text(emojis[i], size=20),
                    ft.Column(controls=[
                        ft.Text(f"Dígito: {t['digito']}", size=14, weight=ft.FontWeight.BOLD, color=color_base),
                        ft.Text(f"{t['veces']} veces ({t['porcentaje']}%)", size=12, color=ft.Colors.GREY_400)
                    ])
                ]),
                padding=10,
                bgcolor=ft.Colors.with_opacity(0.08, color_base),
                border_radius=ft.border_radius.all(10),
                width=180
            ) for i,t in enumerate(data['top_3_calientes'])
        ]
        
        filas = [
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(d), weight=ft.FontWeight.BOLD)),
                ft.DataCell(ft.Text(str(data['frecuencias_detalle'][d]['count']))),
                ft.DataCell(ft.Text(f"{data['frecuencias_detalle'][d]['percentage']:.1f}%"))
            ]) for d in range(10)
        ]
        
        tabla = ft.DataTable(
            columns=[ft.DataColumn(ft.Text("Dígito")), ft.DataColumn(ft.Text("Veces")), ft.DataColumn(ft.Text("%"))],
            rows=filas,
            heading_row_color=ft.Colors.with_opacity(0.1, color_base),
            border=ft.border.all(1, ft.Colors.with_opacity(0.2, ft.Colors.WHITE)),
            border_radius=ft.border_radius.all(10)
        )
        
        return ft.Container(
            content=ft.Column(controls=[
                ft.Text(titulo, size=18, weight=ft.FontWeight.BOLD, color=color_base),
                ft.Text(f"Total: {data['total_analizados']} | Promedio: {data['promedio']}", size=12, color=ft.Colors.GREY_400),
                ft.Divider(height=2),
                ft.Text("🔥 TOP 3 CALIENTES:", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER_300),
                ft.Row(controls=top_items, spacing=10, wrap=True),
                ft.Divider(height=2),
                tabla
            ]),
            padding=20,
            bgcolor=ft.Colors.with_opacity(0.03, ft.Colors.WHITE24),
            border_radius=ft.border_radius.all(15),
            width=float('inf'),
            margin=ft.Margin.only(bottom=15)
        )
    def crear_tarjeta_top10_fijos(self, freq_data):
        """✅ CORREGIDO: Tarjeta Top 10 - Maneja tuplas correctamente"""
        top_10 = freq_data.get('top_10', [])
        total = freq_data.get('total_fijos_unicos', 0)
        
        # ✅ CORREGIDO: mas_repetido es una tupla (fijo, veces), no dict
        mas_rep = freq_data.get('mas_repetido', None)
        if mas_rep and isinstance(mas_rep, tuple) and len(mas_rep) >= 2:
            fijo_num1, veces_num1 = mas_rep[0], mas_rep[1]
        else:
            fijo_num1 = '?'
            veces_num1 = '?'
        
        cards = []
        for i, item in enumerate(top_10):
            # ✅ Cada item es un dict con claves: fijo, veces, porcentaje, ultima_fecha, sorteos_atras
            fijo = item.get('fijo', '?')
            veces = item.get('veces', 0)
            ranking = i + 1
            
            emojis = ['🥇', '🥈', '🥉', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
            
            # Porcentaje real calculado
            porcentaje_real = (veces / total * 100) if total > 0 else 0
            
            cards.append(ft.Container(
                content=ft.Column(controls=[
                    ft.Row(controls=[
                        ft.Text(emojis[i] if i < 10 else str(ranking), size=20),
                        ft.Text(f"{fijo:02d}", size=28, weight=ft.FontWeight.BOLD, 
                              font_family="monospace", color=ft.Colors.CYAN_200),
                        ft.Container(width=10),
                        ft.Column(controls=[
                            ft.Text(f"{veces} veces", size=12, color=ft.Colors.GREY_400),
                            ft.Text(f"{porcentaje_real:.1f}%", size=14, weight=ft.FontWeight.BOLD, 
                                  color=ft.Colors.GREEN_300),
                            ft.Text(f"Último: {item.get('ultima_fecha', 'N/A')}", 
                                  size=10, color=ft.Colors.GREY_500),
                            ft.Text(f"Hace {item.get('sorteos_atras', '?')} sorteos", 
                                  size=10, color=ft.Colors.AMBER_300)
                        ], horizontal_alignment=ft.CrossAxisAlignment.END)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    
                    ft.ProgressBar(
                        value=min(porcentaje_real / 20, 1.0),
                        height=6,
                        color=ft.Colors.AMBER_400 if i < 3 else ft.Colors.BLUE_300,
                        bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE)
                    )
                ], spacing=4),
                width=200,
                padding=12,
                bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.AMBER) if i < 3 else ft.Colors.with_opacity(0.05, ft.Colors.WHITE24),
                border_radius=12,
                border=ft.border.all(1, ft.Colors.AMBER_300) if i < 3 else ft.Border(),
                alignment=ft.Alignment.CENTER
            ))
        
        return ft.Container(
            content=ft.Column(controls=[
                ft.Row(controls=[
                    ft.Icon(ft.Icons.LEADERBOARD, size=22, color=ft.Colors.AMBER_300),
                    # ✅ CORREGIDO: Acceder a tupla con índice [0]
                    ft.Text(f"Total únicos: {total} | Más repetido: {fijo_num1:02d} ({veces_num1}x)", 
                              size=13, color=ft.Colors.GREY_400)
                ], spacing=10),
                ft.Divider(height=1),
                ft.Row(controls=cards, wrap=True, spacing=8, alignment=ft.MainAxisAlignment.CENTER)
            ]),
            padding=20,
            bgcolor=ft.Colors.with_opacity(0.03, ft.Colors.WHITE24),
            border_radius=15,
            width=float('inf')
        )
    def crear_tarjeta_cuadrantes(self, data):
        dom = data['cuadrante_dominante']
        cards = []
        for q,info in data['detalle_por_cuadrante'].items():
            es_dom = q == dom['numero']
            cards.append(ft.Container(
                content=ft.Column(controls=[
                    ft.Text(f"Q{q}", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER_300 if es_dom else ft.Colors.GREY_400),
                    ft.Text(info['rango'], size=14, color=ft.Colors.GREY_400),
                    ft.Divider(height=1),
                    ft.Text(f"{info['count']}", size=16, weight=ft.FontWeight.BOLD),
                    ft.Text(f"{info['porcentaje']}%", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_300 if es_dom else ft.Colors.WHITE),
                    *([ft.Text("🏆 DOMINANTE", size=11, color=ft.Colors.AMBER_300)] if es_dom else [])
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                width=150,
                padding=20,
                bgcolor=ft.Colors.with_opacity(0.15, ft.Colors.AMBER) if es_dom else ft.Colors.with_opacity(0.05, ft.Colors.WHITE24),
                border_radius=ft.border_radius.all(15),
                border=ft.border.all(2, ft.Colors.AMBER_300) if es_dom else ft.Border(),
                alignment=ft.Alignment.CENTER
            ))
        
        return ft.Container(
            content=ft.Column(controls=[
                ft.Text("📐 CUADRANTES", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN_300),
                ft.Text(f"🏆 DOMINANTE: Q{dom['numero']} ({dom['rango']}) - {dom['porcentaje']}%", size=14, color=ft.Colors.AMBER_300, weight=ft.FontWeight.BOLD),
                ft.Divider(height=2),
                ft.Row(controls=cards, alignment=ft.MainAxisAlignment.CENTER, spacing=15, wrap=True)
            ]),
            padding=25,
            bgcolor=ft.Colors.with_opacity(0.03, ft.Colors.WHITE24),
            border_radius=ft.border_radius.all(15),
            width=float('inf')
        )
    
    def crear_tarjeta_tendencias(self, tend, pat):
        tend_color = (
            ft.Colors.GREEN_400 if tend['direccion_dominante']=='SUBIENDO'
            else ft.Colors.RED_400 if tend['direccion_dominante']=='BAJANDO'
            else ft.Colors.GREY_400
        )
        return ft.Container(
            content=ft.Column(controls=[
                ft.Text("📈 TENDENCIAS", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN_300),
                ft.Divider(height=2),
                ft.Container(
                    content=ft.Column(controls=[
                        ft.Text("DIRECCIÓN DOMINANTE", size=12, color=ft.Colors.GREY_500),
                        ft.Text(tend['direccion_dominante'], size=36, weight=ft.FontWeight.BOLD, color=tend_color)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    width=250,
                    padding=20,
                    bgcolor=ft.Colors.with_opacity(0.08, tend_color),
                    border_radius=ft.border_radius.all(15),
                    alignment=ft.Alignment.CENTER
                ),
                ft.Divider(height=2),
                ft.Row(controls=[
                    self.crear_stat_box("ÚLTIMO", tend['ultimo_movimiento'], ft.Colors.BLUE_300),
                    self.crear_stat_box("MAGNITUD", str(tend.get('magnitud_ultimo',0)), ft.Colors.PURPLE_300),
                    self.crear_stat_box("SUBIDAS", f"{tend['porcentaje_subidas']}%", ft.Colors.GREEN_300),
                    self.crear_stat_box("BAJADAS", f"{tend['porcentaje_bajadas']}%", ft.Colors.RED_300),
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=15, scroll="auto", expand=True),
                ft.Divider(height=2),
                ft.Text("📜 PATRONES RECIENTES", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER_300),
                ft.Container(
                    content=ft.Column(controls=[
                        ft.Text(f"Decenas: {pat['ultimos_10_decenas']}", size=13, color=ft.Colors.CYAN_200),
                        ft.Text(f"Unidades: {pat['ultimos_10_unidades']}", size=13, color=ft.Colors.GREEN_200)
                    ]),
                    padding=15,
                    bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE24),
                    border_radius=ft.border_radius.all(10),
                    width=float('inf')
                )
            ]),
            padding=25,
            bgcolor=ft.Colors.with_opacity(0.03, ft.Colors.WHITE24),
            border_radius=ft.border_radius.all(15),
            width=float('inf')
        )
    
    def crear_tarjeta_serie(self, serie, pp):
        if serie['recomendar']:
            numeros = serie.get('serie_parcial', serie['serie'])
            chips = [ft.Container(
                content=ft.Text(f"{n:02d}", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK if n==pp['fijo'] else ft.Colors.WHITE),
                width=50, height=50,
                bgcolor=ft.Colors.AMBER_300 if n==pp['fijo'] else ft.Colors.with_opacity(0.3, ft.Colors.GREEN),
                border_radius=ft.border_radius.all(10),
                alignment=ft.Alignment.CENTER,
                border=ft.border.all(2, ft.Colors.AMBER) if n==pp['fijo'] else ft.Border()
            ) for n in numeros]
            
            contenido = ft.Column(controls=[
                ft.Container(
                    content=ft.Column(controls=[
                        ft.Row(controls=[
                            ft.Icon(ft.Icons.LOCAL_FIRE_DEPARTMENT, size=40, color=ft.Colors.RED_400),
                            ft.Text("!!! SERIE RECOMENDADA !!!", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.RED_300)
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        ft.Text("Decena dentro del cuadrante dominante", size=13, color=ft.Colors.GREY_400)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=20,
                    bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.RED),
                    border_radius=ft.border_radius.all(15),
                    width=float('inf'),
                    alignment=ft.Alignment.CENTER
                ),
                ft.Divider(height=2),
                ft.Row(controls=[
                    self.crear_stat_box("DECENA", str(serie['decena']), ft.Colors.PURPLE_300),
                    self.crear_stat_box("RANGO", serie['serie_str'], ft.Colors.BLUE_300),
                    self.crear_stat_box("CUADRANTE", f"Q{serie['cuadrante_objetivo']}", ft.Colors.ORANGE_300),
                    self.crear_stat_box("ESTADO", "✅ DENTRO", ft.Colors.GREEN_300),
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=15, scroll="auto", expand=True),
                ft.Divider(height=2),
                ft.Text("🎯 NÚMEROS:", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER_300),
                ft.Container(
                    content=ft.Row(controls=chips, spacing=8, wrap=True, alignment=ft.MainAxisAlignment.CENTER),
                    padding=20,
                    bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE24),
                    border_radius=ft.border_radius.all(15),
                    width=float('inf'),
                    alignment=ft.Alignment.CENTER
                ),
                ft.Text(f"Cobertura: {len(numeros)}/10 números", size=12, color=ft.Colors.GREY_400),
                ft.Text("🎲 Probabilidad ~10% vs 1% único", size=12, color=ft.Colors.GREEN_300, weight=ft.FontWeight.BOLD)
            ])
        else:
            contenido = ft.Column(controls=[
                ft.Container(
                    content=ft.Column(controls=[
                        ft.Icon(ft.Icons.WARNING_ROUNDED, size=60, color=ft.Colors.ORANGE_300),
                        ft.Text("⚠️ SERIE NO APLICABLE", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_300),
                        ft.Divider(height=2),
                        ft.Text(serie['razon'], size=12, color=ft.Colors.GREY_500),
                        ft.Text(f"Mantener: {pp['fijo']:02d}", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN_300)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=30,
                    bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.ORANGE),
                    border_radius=ft.border_radius.all(15),
                    width=float('inf'),
                    alignment=ft.Alignment.CENTER
                )]
            )
        
        return ft.Container(
            content=ft.Column(controls=[
                ft.Text("🆕 ESTRATEGIA DE SERIE", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.RED_300),
                ft.Divider(height=2),
                contenido
            ]),
            padding=25,
            bgcolor=ft.Colors.with_opacity(0.03, ft.Colors.WHITE24),
            border_radius=ft.border_radius.all(15),
            width=float('inf')
        )
    
    def crear_tarjeta_resumen(self, meta, prediction):
        pp = prediction['principal']
        serie = prediction['estrategia_serie']
        estrats = prediction['estrategias']
        
        alts_str = ', '.join(f"{a['fijo']:02d}" for a in prediction['alternativas'][:2])
        
        datos_resumen = [
            ("FIJO PRINCIPAL", f"{pp['fijo']:02d}"),
            ("ALTERNATIVAS", alts_str),
            ("CENTENA", str(pp['centena'])),
            ("DECENA", str(pp['decena'])),
            ("UNIDAD", str(pp['unidad'])),
            ("CUADRANTE", f"Q{pp['cuadrante']} ({'00-24' if pp['cuadrante']==1 else '25-49' if pp['cuadrante']==2 else '50-74' if pp['cuadrante']==3 else '75-99'})"),
            ("CONFIANZA", f"{prediction['confianza_global']}%"),
            ("SERIE", f"Decena {serie['decena']} → {serie.get('serie_str','N/A')}"),
            ("MODO", meta['modo']),
            ("REGISTROS", str(meta['total_registros']) if not meta['n_recientes'] else f"Últimos {meta['n_recientes']}")
        ]
        
        filas = [ft.DataRow(cells=[
            ft.DataCell(ft.Text(row[0], weight=ft.FontWeight.BOLD, size=13, color=ft.Colors.AMBER_300)),
            ft.DataCell(ft.Text(row[1], weight=ft.FontWeight.BOLD, size=13, color=ft.Colors.CYAN_300))
        ]) for row in datos_resumen]
        
        estrat_cards = []
        for tipo,est in estrats.items():
            color_map = {'conservadora':(ft.Colors.GREEN,'🟢'), 'balanceada':(ft.Colors.AMBER,'🟡'), 'agresiva':(ft.Colors.RED,'🔴')}
            color,icono = color_map[tipo]
            estrat_cards.append(ft.Container(
                content=ft.Column(controls=[
                    ft.Text(f"{icono} {est['nombre']}", size=14, weight=ft.FontWeight.BOLD, color=color),
                    ft.Text(est['descripcion'], size=11, color=ft.Colors.GREY_400),
                    *([ft.Text(f"Números: {est['numeros']}", size=10, color=ft.Colors.CYAN_200)] if 'numeros' in est else []),
                    ft.Text(f"Riesgo: {est['riesgo']}", size=10, color=color, weight=ft.FontWeight.BOLD)
                ]),
                width=280,
                padding=15,
                bgcolor=ft.Colors.with_opacity(0.08, color),
                border_radius=ft.border_radius.all(12),
                border=ft.border.all(1, color)
            ))
        
        return ft.Container(
            content=ft.Column(controls=[
                ft.Text("⚡ RESUMEN EJECUTIVO", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER_300),
                ft.Divider(height=2),
                ft.DataTable(
                    columns=[ft.DataColumn(ft.Text("PARÁMETRO")), ft.DataColumn(ft.Text("VALOR"))],
                    rows=filas,
                    heading_row_color=ft.Colors.with_opacity(0.15, ft.Colors.AMBER),
                    border=ft.border.all(1, ft.Colors.with_opacity(0.2, ft.Colors.WHITE)),
                    border_radius=ft.border_radius.all(10),
                    column_spacing=30
                ),
                ft.Container(height=20),
                ft.Text("🎮 ESTRATEGIAS DISPONIBLES", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN_300),
                ft.Row(controls=estrat_cards, spacing=15, wrap=True),
                ft.Container(height=20),
                ft.Text("🌴 ¡BUENA SUERTE! 🍀", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_300)
            ]),
            padding=25,
            bgcolor=ft.Colors.with_opacity(0.03, ft.Colors.WHITE24),
            border_radius=ft.border_radius.all(15),
            width=float('inf')
        )
    
    def mostrar_todo(self, e):
        """Mostrar pantalla de bienvenida"""
        self.contenedor_resultados.controls.clear()
        self.contenedor_resultados.controls.append(
            ft.Container(
                padding=40,
                bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE24),
                border_radius=ft.border_radius.all(20),
                width=float('inf'),
                content=ft.Column(controls=[
                    ft.Icon(ft.Icons.INFO_ROUNDED, size=80, color=ft.Colors.CYAN_300),
                    ft.Text("BIENVENIDO AL PREDICTOR", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ft.Text("Configura los parámetros y presiona 'Analizar'", size=14, color=ft.Colors.GREY_400),
                    ft.Divider(height=20),
                    ft.Text("✨ Características:", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER_300),
                    ft.Text("• Análisis Centena/Decena/Unidad", color=ft.Colors.GREY_300),
                    ft.Text("• Top 10 Fijos frecuentes", color=ft.Colors.GREY_300),
                    ft.Text("• Análisis de Cuadrantes (00-99)", color=ft.Colors.GREY_300),
                    ft.Text("• Detección de Tendencias", color=ft.Colors.GREY_300),
                    ft.Text("• Estrategia de Serie de Decena", color=ft.Colors.GREY_300),
                    ft.Text("• Predicción con Confianza %", color=ft.Colors.GREY_300)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            )
        )
        self.page.update()


# ============================================
# 🚀 FUNCIÓN PRINCIPAL
# ============================================

def main(page: ft.Page):
    """Función principal"""
    FloridaPredictorApp(page)


if __name__ == "__main__":
    ft.run(main)
