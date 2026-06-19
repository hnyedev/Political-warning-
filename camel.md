# CAMEL-OASIS MX Surveillance Simulation
## Research Brief & Cursor Build Instructions

> **Contexto:** Hackathon de AI Safety — Simulación de sistemas de monitoreo masivo  
> **Objetivo:** Modelar cómo un clasificador estatal (inspirado en arquitecturas documentadas como IJOP)  
> procesaría población sintética mexicana, medir sus tasas de error y generar *political warnings* cuantificables.  
> **Dataset:** `latam-gpt/personas` (HuggingFace) — subconjunto LATAM del PersonaHub de 1B personas  
> **Framework:** CAMEL multi-agent + OASIS social simulation  
> **Output final:** Reporte técnico con métricas (FPR, recall, chilling effect index, political warning score)

---

## Cómo usar este documento (living spec)

`camel.md` es la **fuente de verdad de investigación**. El código en `pipeline/` implementa lo que aquí está especificado; cuando la investigación avance, **actualiza este archivo primero** y luego el código.

| Sección | Cuándo editarla |
|---|---|
| **Estado actual de la investigación** | Después de cada corrida, hallazgo, o cambio de hipótesis |
| **Hipótesis activas** | Al formular o descartar una hipótesis |
| **Preguntas abiertas** | Cuando surja una duda que bloquee o guíe el diseño |
| **Bitácora de decisiones** | Cada decisión metodológica importante (con fecha) |
| **Changelog de investigación** | Resumen breve por sesión de trabajo |
| **FASE N — …** | Cuando la spec de implementación de una fase cambie |
| **Notas críticas** | Cuando descubramos un sesgo o limitación nueva |

**Convenciones de estado:** `🔴 pendiente` · `🟡 en progreso` · `🟢 implementado` · `🔵 validado con datos` · `⚪ descartado`

**Setup y ejecución:** ver [`README.md`](./README.md) — este documento no duplica pasos de instalación.

---

## Estado actual de la investigación

> *Última actualización: 2025-06-19 · Modificar en cada sesión de research.*

### Resumen ejecutivo (1 párrafo)

Infraestructura del pipeline completa (p01–p06): esquema `PersonaProfile`, rule engine IJOP-like, minería de asociación (Apriori / FP-Growth / ECLAT), agentes CAMEL stub, métricas de evaluación y generador de reporte. **Pendiente:** corrida end-to-end con datos reales de PersonaHub + extracción Ollama, validación de FPR sobre categorías protegidas, y refinamiento del citizen agent para chilling effect.

### Mapa de fases

| Fase | Módulo | Estado | Artefacto esperado | Notas |
|---|---|---|---|---|
| 1 | `pipeline/p01_persona_extraction/` | 🟡 en progreso | `data/processed/personas_structured.jsonl` | Download listo; extractor Ollama sin corrida a escala |
| 2 | `pipeline/p02_graph_construction/` | 🟢 implementado | `data/synthetic_graph/social_graph.graphml` | Aristas por ≥2 atributos compartidos |
| 3 | `pipeline/p03_surveillance_classifier/` | 🟢 implementado | scores en perfiles | Rule engine + association runner |
| 4 | `pipeline/p04_camel_agents/` | 🟡 en progreso | acciones simuladas por persona | Stubs funcionales; chilling effect simplificado |
| 5 | `pipeline/p05_evaluation/` | 🟢 implementado | `reports/evaluation_report.json` | KPI: `protected_false_positive_rate` |
| 6 | `pipeline/p06_report/` | 🟢 implementado | `reports/technical_report.md` | Plantilla Jinja2; PDF pendiente |

### Hipótesis activas

| ID | Hipótesis | Cómo falsarla | Estado |
|---|---|---|---|
| H1 | La regla `uses_encrypted_apps` produce FPR estructural >40% en población MX | Medir `whatsapp_bias_rate` sobre muestra 10k | 🟡 sin medir |
| H2 | FP-Growth encuentra más reglas sesgadas hacia protegidos que Apriori | Comparar `protected_bias_score` en `algorithm_comparison` | 🟡 sin medir |
| H3 | PageRank >0.7 eleva falsos positivos en periodistas bien conectados | Cruzar `journalist_flag_rate` con centralidad | 🔴 pendiente |
| H4 | El chilling effect es mayor en activistas que en población general | Comparar `modified_due_to_surveillance` por `political_activity` | 🔴 pendiente |

### Preguntas abiertas

- [ ] ¿El dataset `latam-gpt/personas` incluye metadatos de idioma confiables para filtrar es-MX?
- [ ] ¿WhatsApp debe modelarse explícitamente vs. `uses_encrypted_apps` genérico?
- [ ] ¿Qué ground truth sintético usar para `recall_on_synthetic_threats`?
- [ ] ¿Integrar CAMEL-AI completo o mantener agentes determinísticos ligeros para reproducibilidad?
- [ ] ¿Umbral de PageRank 0.7 es válido en grafos sparse de 10k nodos?

### State of the art (enfoque actual — modificable)

Documento vivo: **actualizar cuando cambie la estrategia metodológica.**

| Dimensión | Enfoque elegido | Alternativas consideradas | Por qué (por ahora) |
|---|---|---|---|
| Población | 10k personas streaming desde HuggingFace | Dataset completo 1B | Viabilidad hackathon; significancia estadística básica |
| Extracción | Ollama local, JSON estricto, batches 50 | API cloud, NER clásico | Privacidad, costo cero, control de prompt |
| Grafo | NetworkX no-dirigido, pesos por atributos compartidos | GNN (PyG, DGL) | Interpretabilidad; GNN reservado para iteración futura |
| Clasificación | Reglas explícitas + asociación (sin causal inference) | ML supervisado end-to-end | Separar reglas auditables vs. patrones opacos — objetivo del research |
| Asociación | Apriori + FP-Growth + ECLAT (mlxtend + tidsets) | Spark MLlib, ARM en GPU | Pure Python, reproducible, comparable entre algoritmos |
| Simulación | 3 agentes (citizen / classifier / auditor) | OASIS full social sim | Scope acotado; extensible a OASIS en fase 2 del research |
| Evaluación | FPR protegidos + WhatsApp bias + chilling index | Solo accuracy | Métricas políticamente relevantes, no solo ML |
| Sesgo WhatsApp | Regla explícita en YAML + métrica dedicada | Excluir WhatsApp del flag | Demostrar sesgo estructural IJOP-like — core del proyecto |

### Bitácora de decisiones

| Fecha | Decisión | Rationale |
|---|---|---|
| 2025-06-19 | Prefijos `p01`–`p06` en carpetas pipeline | Python no importa módulos `01_*` |
| 2025-06-19 | No implementar inferencia causal en v1 | Demostrar peligro de correlación pura |
| 2025-06-19 | `protected_false_positive_rate` como KPI principal | Art. 6 y 7 CPEUM — categorías protegidas |
| 2025-06-19 | Rule engine determinístico | Reproducibilidad para auditoría |

### Changelog de investigación

| Fecha | Cambio |
|---|---|
| 2025-06-19 | Bootstrap infraestructura: config YAML, pipeline p01–p06, `run_pipeline.py`, README |

---

## Arquitectura General del Pipeline

```
latam-gpt/personas (HuggingFace)
        ↓
[FASE 1] Extracción de Atributos
  → LLM local (Ollama) extrae atributos estructurados de cada persona en texto libre
        ↓
[FASE 2] Construcción de Grafo Social
  → NetworkX conecta personas por atributos compartidos
  → Scores de centralidad (PageRank, betweenness, degree)
        ↓
[FASE 3] Clasificador de Vigilancia (Reglas + ML)
  → Rule engine IJOP-like adaptado a México
  → Algoritmos de asociación: Apriori, FP-Growth, ECLAT
  → Risk scorer compuesto (0-100)
        ↓
[FASE 4] Simulación Multi-Agente CAMEL
  → citizen_agent: comportamiento bajo vigilancia
  → classifier_agent: evalúa y clasifica
  → auditor_agent: detecta FP y chilling effect
        ↓
[FASE 5] Evaluación y Métricas
  → FPR sobre categorías protegidas constitucionalmente
  → Recall del clasificador sobre amenazas sintéticas
  → Political Warning Index
        ↓
[FASE 6] Reporte Técnico
  → Markdown → PDF con métricas, hallazgos y recomendaciones
```

---

## Estructura de Directorios

> **Implementación actual:** carpetas `p01`–`p06` (nombres importables en Python). Ver mapa de fases arriba para estado.

```
Political-warning/
├── README.md                       # Setup, arquitectura, métricas (GitHub)
├── camel.md                        # ← ESTE ARCHIVO — living research spec
├── requirements.txt
├── run_pipeline.py
├── config/
│   ├── classifier_rules.yaml
│   └── association_config.yaml
├── data/
│   ├── raw/                        # PersonaHub descargado (parquet)
│   ├── processed/                  # Personas estructuradas (jsonl)
│   └── synthetic_graph/            # Grafo social (GraphML)
├── pipeline/
│   ├── common/                     # paths.py, config.py
│   ├── p01_persona_extraction/
│   ├── p02_graph_construction/
│   ├── p03_surveillance_classifier/
│   │   └── association_algorithms/
│   ├── p04_camel_agents/
│   ├── p05_evaluation/
│   └── p06_report/
├── notebooks/
│   └── exploratory_analysis.ipynb
└── reports/
    ├── evaluation_report.json
    └── technical_report.md
```

---

## FASE 1 — Extracción de Atributos de PersonaHub

### Contexto para Cursor
El dataset `latam-gpt/personas` contiene descripciones de personas en texto libre (ej: *"Una periodista de investigación en Ciudad de México que cubre corrupción gubernamental y usa Signal para proteger a sus fuentes"*). El objetivo de esta fase es convertir ese texto en un esquema estructurado que el clasificador pueda procesar.

### Instrucciones a Cursor

**Archivo: `pipeline/p01_persona_extraction/schema.py`**

Construir un dataclass Pydantic `PersonaProfile` con los siguientes atributos. Todos los atributos extraídos deben ser `Optional` porque el LLM puede no inferirlos de todos los textos:

```python
# Atributos de identidad
persona_id: str
raw_text: str
language_detected: str          # "es-MX", "es-419", etc.

# Atributos de comportamiento digital
uses_vpn: Optional[bool]
uses_encrypted_apps: Optional[bool]   # Signal, Telegram, Wire (NO WhatsApp — ver nota)
uses_tor: Optional[bool]
digital_activity_level: Optional[str] # "low", "medium", "high"

# Atributos socio-políticos
occupation: Optional[str]
political_activity: Optional[str]     # "journalist", "activist", "opposition",
                                      # "government", "none", "unknown"
religious_activity: Optional[str]     # "none", "moderate", "organized", "frequent"
international_contacts: Optional[bool]
location_mx: Optional[str]            # Estado mexicano si se puede inferir

# Atributos de red (se llenan en Fase 2)
graph_centrality: Optional[float]
betweenness_centrality: Optional[float]
pagerank_score: Optional[float]

# Scores de clasificación (se llenan en Fase 3)
risk_score: Optional[float]           # 0.0 - 100.0
risk_category: Optional[str]          # "low", "medium", "high", "flagged"
association_rules_triggered: Optional[list[str]]  # ← reglas de asociación disparadas

# Flags de auditoría (se llenan en Fase 5)
is_constitutionally_protected: Optional[bool]
false_positive_flag: Optional[bool]
chilling_effect_predicted: Optional[bool]
```

> **Nota técnica:** WhatsApp aparece como "herramienta sospechosa" en el clasificador IJOP (ver documento de contexto). En México, WhatsApp es la app de mensajería dominante (~94% penetración). Esto genera un sesgo estructural crítico que el evaluador debe medir explícitamente.

**Archivo: `pipeline/p01_persona_extraction/download_dataset.py`**

- Usar `datasets` de HuggingFace con `streaming=True` para no descargar el dataset completo
- Tomar muestra de **10,000 personas** para el hackathon (estadísticamente significativa)
- Filtrar por idioma español si el dataset tiene metadatos de idioma
- Guardar como `data/raw/personas_sample_10k.parquet`

**Archivo: `pipeline/p01_persona_extraction/attribute_extractor.py`**

- Usar Ollama con el modelo disponible localmente para extraer atributos
- El prompt del sistema debe instruir al LLM a responder ÚNICAMENTE en JSON válido
- Procesar en batches de 50 personas para no saturar memoria
- Guardar resultado en `data/processed/personas_structured.jsonl` (un JSON por línea)
- Implementar retry con backoff exponencial para fallos del LLM local

Prompt template a usar:
```
Dado el siguiente perfil de persona, extrae los atributos en formato JSON.
Responde ÚNICAMENTE con el JSON, sin texto adicional.

Perfil: {raw_text}

Esquema esperado: {schema_json}

Si no puedes inferir un atributo con certeza razonable, usa null.
```

---

## FASE 2 — Construcción del Grafo Social

### Contexto para Cursor
Las GNN (Graph Neural Networks) son el núcleo del análisis de redes sociales en sistemas de vigilancia masiva (ver sección "Análisis de Grafos Sociales" del documento de contexto). OASIS usa grafos para simular propagación de información y detectar nodos de influencia. En esta fase construimos ese grafo desde los atributos extraídos.

### Instrucciones a Cursor

**Archivo: `pipeline/p02_graph_construction/social_graph_builder.py`**

Construir grafo no-dirigido con NetworkX donde:
- **Nodos** = cada `PersonaProfile` (atributos como node attributes)
- **Aristas** = conexión entre dos personas si comparten 2+ atributos de los siguientes:
  - Misma `location_mx`
  - Misma `occupation` o `political_activity`
  - Ambas tienen `uses_encrypted_apps = True`
  - Ambas tienen `international_contacts = True`
  - Mismo nivel de `religious_activity`

El peso de la arista debe ser el número de atributos compartidos (2, 3, 4, o 5).

**Archivo: `pipeline/p02_graph_construction/centrality_scorer.py`**

Calcular y guardar en cada nodo:
- `degree_centrality` — conexiones directas normalizadas
- `betweenness_centrality` — qué tan "puente" es el nodo entre comunidades
- `pagerank_score` — influencia global en la red (análogo a lo que GNN mide)

Umbral de "nodo de alta influencia": `pagerank_score > 0.7` (configurable en `config/classifier_rules.yaml`)

Exportar grafo como `data/synthetic_graph/social_graph.graphml` para visualización posterior.

---

## FASE 3 — Clasificador de Vigilancia

### Contexto para Cursor
Esta es la fase central del research. Implementamos dos capas de clasificación:

1. **Rule engine** — reglas determinísticas inspiradas en el IJOP y adaptadas al contexto legal mexicano (Ley Olimpia, LFPDPPP, uso de VPN legal en México)
2. **Algoritmos de asociación** — minería de patrones frecuentes para descubrir qué combinaciones de atributos el clasificador aprendería automáticamente

La distinción es crítica para el reporte: las reglas explícitas son auditables; los patrones aprendidos por asociación son opacos y potencialmente más peligrosos.

### 3A — Rule Engine

**Archivo: `config/classifier_rules.yaml`**

```yaml
# Clasificador de vigilancia MX-like
# Adaptado de reglas documentadas en IJOP (Xinjiang) + licitación MX

version: "1.0"
context: "Mexico — Monitoreo de medios, prensa, internet y televisión"

# Categorías protegidas constitucionalmente (Art. 6 y 7 CPEUM)
# Un alto FPR sobre estas categorías es la señal de alerta política más importante
protected_categories:
  - "journalist"
  - "human_rights_defender"
  - "political_opposition"
  - "religious_leader"
  - "activist"

# Reglas de riesgo con pesos (suman al risk_score 0-100)
risk_rules:

  critical_triggers:     # Cualquiera de estos sube score 25+ pts
    - attribute: uses_vpn
      value: true
      weight: 25
      note: "Legal en México pero clasificado como sospechoso en sistemas IJOP-like"

    - attribute: uses_tor
      value: true
      weight: 30
      note: "Uso de red de anonimato — máximo nivel de sospecha algorítmica"

    - attribute: international_contacts
      value: true
      weight: 20
      note: "Patrón IJOP: llamadas internacionales como indicador de riesgo"

  medium_triggers:       # Contribuyen 10-20 pts
    - attribute: uses_encrypted_apps
      value: true
      weight: 15
      note: "CRÍTICO: WhatsApp incluido — afecta ~94% de usuarios MX"

    - attribute: political_activity
      values: ["journalist", "activist", "opposition"]
      weight: 20

    - attribute: religious_activity
      values: ["organized", "frequent"]
      weight: 10

  network_triggers:      # Basados en centralidad del grafo
    - attribute: pagerank_score
      threshold: 0.7
      weight: 20
      note: "Nodo de alta influencia en red social"

    - attribute: betweenness_centrality
      threshold: 0.6
      weight: 15
      note: "Puente entre comunidades — vector de propagación"

# Umbrales de categorías de riesgo
thresholds:
  low: 0
  medium: 30
  high: 60
  flagged: 80

# Umbral de alerta política
political_warning:
  protected_fpr_threshold: 0.15   # Si >15% de protegidos son flagged → WARNING
  whatsapp_bias_threshold: 0.40   # Si >40% del total es marcado por encrypted_apps → SESGO CRÍTICO
```

### 3B — Algoritmos de Asociación (NUEVO)

**Contexto para Cursor:** Los algoritmos de asociación descubren reglas del tipo `{A, B} → {C}` en datos transaccionales. Aplicados a perfiles de vigilancia, revelan qué combinaciones de comportamientos el sistema aprendería a correlacionar automáticamente — muchas de ellas sin justificación causal, solo correlacional. Esto es exactamente el tipo de "correlación espuria" que el documento de contexto menciona como riesgo de la Inferencia Causal mal aplicada.

**Archivo: `config/association_config.yaml`**

```yaml
algorithms:
  apriori:
    min_support: 0.05      # Patrón debe aparecer en ≥5% de personas
    min_confidence: 0.6    # Regla debe ser correcta en ≥60% de casos
    min_lift: 1.5          # Regla debe ser 1.5x mejor que azar
    max_itemset_length: 4  # Máximo 4 atributos por regla

  fp_growth:
    min_support: 0.03      # Más sensible que Apriori — detecta patrones raros
    min_confidence: 0.5
    min_lift: 2.0

  eclat:
    min_support: 0.05
    # ECLAT usa intersección de tidsets — más eficiente en memoria
    # Útil para el dataset de 10k personas

# Atributos a usar como "items" para la minería
item_attributes:
  - uses_vpn
  - uses_encrypted_apps
  - uses_tor
  - political_activity       # binarizar: journalist/activist/opposition = True
  - religious_activity       # binarizar: organized/frequent = True
  - international_contacts
  - digital_activity_level   # binarizar: high = True
  - location_mx              # binarizar por región: norte/sur/cdmx
  - high_centrality          # pagerank > 0.7

# Qué medir en cada algoritmo
risk_evaluation:
  target_consequent: "risk_category_flagged"  # La regla dispara clasificación "flagged"
  measure_bias_toward:
    - "political_activity_journalist"
    - "uses_encrypted_apps_true"              # El sesgo de WhatsApp
  compare_lift_vs_protected: true             # ¿Las reglas tienen mayor lift sobre protegidos?
```

**Archivo: `pipeline/p03_surveillance_classifier/association_algorithms/runner.py`**

Implementar los tres algoritmos usando `mlxtend` (puro Python, sin Spark):

```python
# Pseudocódigo para Cursor — implementar completamente

from mlxtend.frequent_patterns import apriori, fpgrowth, association_rules
from mlxtend.preprocessing import TransactionEncoder
import pandas as pd

class AssociationRiskAnalyzer:
    """
    Corre Apriori, FP-Growth y ECLAT sobre los perfiles de personas.
    Mide qué combinaciones de atributos el clasificador aprendería
    a asociar con alto riesgo, y evalúa el sesgo sobre categorías protegidas.
    """
    
    def binarize_profiles(self, profiles: list[PersonaProfile]) -> pd.DataFrame:
        """
        Convierte atributos continuos/categóricos en binarios para minería.
        Cada fila = persona, cada columna = atributo binario.
        """
        pass
    
    def run_apriori(self, df: pd.DataFrame, config: dict) -> pd.DataFrame:
        pass
    
    def run_fpgrowth(self, df: pd.DataFrame, config: dict) -> pd.DataFrame:
        pass
    
    def run_eclat(self, df: pd.DataFrame, config: dict) -> pd.DataFrame:
        """
        mlxtend no tiene ECLAT nativo. Implementar usando intersección
        de sets de transaction IDs (tidsets) manualmente o usar
        la librería pyECLAT como alternativa.
        """
        pass
    
    def evaluate_bias(self, rules: pd.DataFrame, profiles: list) -> dict:
        """
        Para cada regla descubierta:
        - ¿Con qué frecuencia el consecuente afecta categorías protegidas?
        - ¿El lift es significativamente mayor sobre periodistas/activistas?
        - ¿La regla es causalmente plausible o solo correlacional?
        """
        pass
    
    def compare_algorithms(self) -> dict:
        """
        Output comparativo para el reporte:
        - Número de reglas encontradas por algoritmo
        - Reglas de mayor lift
        - Reglas con mayor sesgo sobre protegidos
        - Tiempo de ejecución y uso de memoria
        """
        pass
```

**Archivo: `pipeline/p03_surveillance_classifier/association_algorithms/risk_evaluator.py`**

Métricas específicas a calcular por cada algoritmo:

| Métrica | Descripción | Por qué importa |
|---|---|---|
| `rules_count` | Total de reglas descubiertas | Complejidad del clasificador aprendido |
| `protected_bias_score` | Lift promedio sobre categorías protegidas vs. resto | Discriminación algorítmica |
| `whatsapp_rule_count` | Reglas que incluyen `uses_encrypted_apps` como antecedente | Sesgo estructural por penetración de WhatsApp |
| `causal_plausibility` | % de reglas con justificación causal documentada (manual) | Correlación espuria vs. real |
| `runtime_seconds` | Tiempo de ejecución | Viabilidad operacional del clasificador |
| `memory_mb` | Memoria usada | Viabilidad en infraestructura real |

---

## FASE 4 — Simulación Multi-Agente CAMEL

### Contexto para Cursor
CAMEL (Communicative Agents for "Mind" Exploration of Large Language Model Society) permite simular conversaciones entre agentes con roles definidos. Aquí simulamos la interacción entre el ciudadano bajo vigilancia, el clasificador estatal, y el auditor de derechos digitales.

### Instrucciones a Cursor

**Archivo: `pipeline/p04_camel_agents/citizen_agent.py`**

- El agente recibe un `PersonaProfile` como contexto
- Su rol es simular el comportamiento comunicativo de esa persona (qué publica, con quién interactúa, qué apps usa)
- Debe modelar el **chilling effect**: si el agente "sabe" que es observado, cambia su comportamiento
- Output por persona: lista de acciones simuladas (`[{action, platform, timestamp, modified_due_to_surveillance}]`)

**Archivo: `pipeline/p04_camel_agents/classifier_agent.py`**

- Recibe las acciones del citizen_agent
- Aplica el rule engine y los algoritmos de asociación
- Emite un `ClassificationDecision` con: score, categoría, reglas disparadas, y acción recomendada (`"monitor"`, `"interrogate"`, `"flag"`)
- Debe ser determinístico (mismo input → mismo output) para reproducibilidad

**Archivo: `pipeline/p04_camel_agents/auditor_agent.py`**

- Recibe el `ClassificationDecision` y el `PersonaProfile` original
- Evalúa: ¿Es este un falso positivo? ¿Viola derechos constitucionales?
- Detecta patrones de chilling effect a nivel poblacional
- Output: `AuditReport` por persona con flags de violación

---

## FASE 5 — Evaluación y Métricas

### Contexto para Cursor
Esta fase produce los números que van al reporte técnico. El "ground truth" es sintético: definimos que personas con `political_activity` en categorías protegidas son **verdaderos negativos** (no deberían ser flaggeadas), y simulamos un conjunto de "amenazas reales" como **verdaderos positivos**.

### Instrucciones a Cursor

**Archivo: `pipeline/p05_evaluation/metrics.py`**

Calcular y exportar como JSON:

```python
@dataclass
class EvaluationReport:
    # Métricas del clasificador
    total_population: int
    total_flagged: int
    flag_rate: float                    # % población total marcada
    
    # Métricas de error críticas
    false_positive_rate: float          # FPR general
    protected_false_positive_rate: float # FPR sobre categorías protegidas ← KPI principal
    recall_on_synthetic_threats: float  # Qué tan bien detecta "amenazas reales"
    
    # Métricas de sesgo
    whatsapp_bias_rate: float           # % marcados solo por encrypted_apps
    journalist_flag_rate: float         # % periodistas marcados
    
    # Métricas por algoritmo de asociación
    apriori_metrics: AlgorithmMetrics
    fpgrowth_metrics: AlgorithmMetrics
    eclat_metrics: AlgorithmMetrics
    
    # Chilling effect
    chilling_effect_index: float        # % personas que modificaron comportamiento
    
    # Veredicto final
    political_warning_triggered: bool
    political_warning_reason: str
```

**Archivo: `pipeline/p05_evaluation/algorithm_comparison.py`**

Tabla comparativa de los tres algoritmos de asociación:
- Para cada algoritmo: reglas encontradas, bias score, runtime, memoria
- Identificar qué algoritmo produce clasificadores más sesgados
- Identificar qué algoritmo sería más peligroso si lo adoptara un Estado

---

## FASE 6 — Reporte Técnico

### Instrucciones a Cursor

**Archivo: `pipeline/p06_report/generate_report.py`**

Leer el JSON de `EvaluationReport` y generar un Markdown estructurado con:

1. **Executive Summary** — 3 hallazgos principales en lenguaje accesible
2. **Metodología** — Pipeline resumido, dataset, tamaño de muestra
3. **Resultados del Clasificador** — Tabla de métricas principales
4. **Análisis de Algoritmos de Asociación** — Tabla comparativa Apriori/FP-Growth/ECLAT
5. **Análisis de Sesgo** — Sesgo sobre categorías protegidas, el problema de WhatsApp
6. **Political Warning Index** — Cálculo y justificación
7. **Recomendaciones** — Para reguladores, para la sociedad civil, para defensores digitales
8. **Limitaciones** — Qué no puede decir este estudio (datos sintéticos, simulación)

---

## Requirements

> **Fuente canónica:** [`requirements.txt`](./requirements.txt) en la raíz del repo. La lista siguiente es referencia; si divergen, gana `requirements.txt`.

```txt
# Data
datasets>=2.20.0
pandas>=2.1.0
pyarrow>=14.0.0
pydantic>=2.0.0

# Graph
networkx>=3.2.0

# Association algorithms
mlxtend>=0.23.0
pyECLAT>=1.0.2

# LLM local
ollama>=0.3.0

# CAMEL framework
camel-ai>=0.2.0

# Evaluation
scikit-learn>=1.4.0
numpy>=1.26.0

# Report
jinja2>=3.1.0
```

---

## Notas Críticas para el Research

### El problema de WhatsApp (sesgo estructural MX)
WhatsApp aparece como "herramienta sospechosa" en el clasificador IJOP documentado. En México, ~94% de usuarios de internet usan WhatsApp. Un clasificador que herede esta regla marcaría a prácticamente toda la población adulta conectada. **Esta es la demostración más poderosa de falso positivo estructural que puede producir este estudio.**

### Limitación de datos sintéticos
Los perfiles de PersonaHub son generados por LLMs. Pueden sobrerepresentar ciertos perfiles (activistas, periodistas) si el LLM tiene sesgos de entrenamiento. El reporte debe documentar esta limitación explícitamente.

### Sobre los algoritmos de asociación
- **Apriori** es el más interpretable pero el más lento — ideal para auditoría
- **FP-Growth** es más eficiente y encuentra reglas que Apriori puede perder — más parecido a lo que usaría un sistema real
- **ECLAT** es eficiente en memoria — relevante para infraestructura de bajo costo (más accesible para Estados con menor capacidad técnica)
- La comparación entre los tres responde: *¿qué tan diferente sería el clasificador según el algoritmo elegido?*

### Sobre causalidad vs. correlación
Las reglas de asociación descubren correlaciones, no causalidades. El documento de contexto menciona que la Inferencia Causal se usa en sistemas reales para "distinguir correlaciones espurias de causalidades reales". Esta simulación deliberadamente NO implementa inferencia causal — para demostrar qué pasa cuando un clasificador solo mina asociaciones sin validación causal. Eso es exactamente lo que hace más peligroso un sistema real.

---

*Generado para hackathon de AI Safety — Investigación sobre sistemas de monitoreo masivo y political warnings*  
*Dataset: latam-gpt/personas (HuggingFace) | Framework: CAMEL-AI + OASIS*

**Mantenimiento:** al cerrar cada sesión de research, actualizar *Estado actual de la investigación* (arriba) y el *Changelog*. Setup y comandos → [`README.md`](./README.md).