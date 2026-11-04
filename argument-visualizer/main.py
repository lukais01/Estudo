import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config
from src.data_loader import load_data
from src.graph_builder import build_graph
from src.analyzer import analyze_graph
from src.toulmin import TOULMIN_LABELS, component_color, component_shape

st.set_page_config(page_title="Argument Visualizer", page_icon="🧩", layout="wide")
st.title("🧩 Argument Visualizer")
st.caption("Visualização e exploração de redes argumentativas estruturadas pelo modelo de Toulmin.")

with st.sidebar:
    st.header("Dados da discussão")
    uploaded = st.file_uploader("Enviar arquivo JSON", type=["json"])
    st.divider()
    st.markdown("**Modelo de Toulmin**")
    st.write("Claim · Grounds · Warrant · Backing · Qualifier · Rebuttal")

if uploaded is None:
    st.info("Envie um JSON para construir a rede argumentativa.")
    with st.expander("Exemplo de estrutura JSON"):
        st.code('''{
  "metadata": {"title": "Discussão"},
  "arguments": [
    {"id":"C1", "text":"A conclusão defendida.", "type":"claim"},
    {"id":"D1", "text":"Um dado que sustenta a conclusão.", "type":"grounds"},
    {"id":"W1", "text":"A regra que conecta o dado à conclusão.", "type":"warrant"}
  ],
  "relations": [
    {"source":"D1", "target":"C1", "type":"supports"},
    {"source":"W1", "target":"C1", "type":"warrants"}
  ]
}''', language="json")
    st.stop()

try:
    metadata, arguments, relations = load_data(uploaded)
    graph = build_graph(arguments, relations)
    metrics = analyze_graph(graph)
except (ValueError, KeyError, TypeError) as exc:
    st.error(f"Não foi possível processar o JSON: {exc}")
    st.stop()

st.subheader(metadata.get("title") or "Análise de argumentos")
if metadata.get("source"):
    st.caption(f"Fonte: {metadata['source']}")
if metadata.get("description"):
    st.write(metadata["description"])

kpis = st.columns(5)
kpis[0].metric("Argumentos", metrics["arguments"])
kpis[1].metric("Relações", metrics["relations"])
kpis[2].metric("Elementos Toulmin", metrics["components_used"])
kpis[3].metric("Nós isolados", metrics["isolated_count"])
kpis[4].metric("Densidade", f"{metrics['density']:.3f}")

with st.expander("Filtros da visualização", expanded=True):
    c1, c2, c3 = st.columns(3)
    components = sorted({a.toulmin_component for a in arguments})
    stances = sorted({(a.stance or "unspecified") for a in arguments})
    chosen_components = c1.multiselect("Componentes de Toulmin", components, default=components,
        format_func=lambda x: TOULMIN_LABELS.get(x, x.title()))
    chosen_stances = c2.multiselect("Posicionamento", stances, default=stances,
        format_func=lambda x: {"pro":"A favor", "con":"Contrário", "neutral":"Neutro", "unspecified":"Não informado"}.get(x, x.title()))
    show_labels = c3.checkbox("Exibir rótulos das relações", value=True)

visible = {a.id for a in arguments if a.toulmin_component in chosen_components and (a.stance or "unspecified") in chosen_stances}
visible_relations = [r for r in relations if r.source in visible and r.target in visible]
tabs = st.tabs(["🕸️ Rede interativa", "🏛️ Estrutura de Toulmin", "Argumentos", "Relações", "Análise"])

with tabs[0]:
    st.subheader("Mapa de relações argumentativas")
    st.caption("A cor e a forma do nó indicam o componente de Toulmin. A cor da aresta indica o tipo de relação. A seta representa source → target.")
    if not visible:
        st.warning("Os filtros selecionados não retornaram argumentos.")
    else:
        nodes = []
        for a in arguments:
            if a.id not in visible: continue
            degree = graph.degree(a.id)
            size = min(48, 20 + degree * 4)
            label = f"{a.id}\n{TOULMIN_LABELS.get(a.toulmin_component, a.toulmin_component)}"
            nodes.append(Node(id=a.id, label=label, size=size,
                              color=component_color(a.toulmin_component),
                              shape=component_shape(a.toulmin_component)))
        edges = []
        for r in visible_relations:
            attack = r.relation_type in {"attacks", "rebuts", "undercuts", "challenges"}
            edges.append(Edge(source=r.source, target=r.target,
                              label=r.relation_type if show_labels else "",
                              color="#D9485F" if attack else "#368A70",
                              width=3 if attack else 2))
        config = Config(width="100%", height=700, directed=True, physics=True,
                        hierarchical=False, nodeHighlightBehavior=True,
                        highlightColor="#F4C95D", collapsible=False,
                        staticGraph=False)
        selected = agraph(nodes=nodes, edges=edges, config=config)
        selected_id = selected if isinstance(selected, str) else selected.get("id") if isinstance(selected, dict) else None
        with st.expander("Legenda", expanded=False):
            legend = st.columns(3)
            for i, (key, label) in enumerate(TOULMIN_LABELS.items()):
                legend[i % 3].markdown(f"<span style='color:{component_color(key)}'>●</span> {label}", unsafe_allow_html=True)
            st.markdown("🟢 Apoio / relação não adversarial &nbsp;&nbsp; 🔴 Ataque, refutação ou contestação", unsafe_allow_html=True)
        if selected_id in graph:
            attrs = graph.nodes[selected_id]
            st.divider()
            st.subheader(f"Argumento selecionado: {selected_id}")
            left, right = st.columns([2, 1])
            left.write(attrs.get("text", "Texto não informado."))
            left.caption(f"Autor: {attrs.get('author') or 'Não informado'}")
            right.write(f"**Elemento:** {TOULMIN_LABELS.get(attrs.get('toulmin_component'), 'Não classificado')}")
            right.write(f"**Posicionamento:** {attrs.get('stance') or 'Não informado'}")
            if attrs.get("qualifier"): right.write(f"**Qualificador:** {attrs['qualifier']}")
            inc, out = st.columns(2)
            incoming = list(graph.in_edges(selected_id, data=True))
            outgoing = list(graph.out_edges(selected_id, data=True))
            with inc:
                st.markdown("**Relações recebidas**")
                for u, v, d in incoming: st.write(f"{u} → {v} · {d.get('relation_type')}")
                if not incoming: st.caption("Nenhuma relação recebida.")
            with out:
                st.markdown("**Relações enviadas**")
                for u, v, d in outgoing: st.write(f"{u} → {v} · {d.get('relation_type')}")
                if not outgoing: st.caption("Nenhuma relação enviada.")
        else:
            st.info("Clique em um nó para consultar seu conteúdo e suas conexões.")

with tabs[1]:
    st.subheader("Estrutura do argumento segundo Toulmin")
    st.write("A conclusão é sustentada por dados; a garantia explica a passagem dos dados à conclusão; o backing fundamenta a garantia; o qualifier delimita a força da conclusão; e o rebuttal registra exceções ou condições que podem enfraquecê-la.")
    descriptions = {
        "claim":"Conclusão ou tese que se pretende defender.",
        "grounds":"Dados, fatos, exemplos ou evidências apresentados.",
        "warrant":"Regra ou princípio que conecta os dados à conclusão.",
        "backing":"Fundamentação adicional que sustenta a garantia.",
        "qualifier":"Grau de força, probabilidade ou limite da conclusão.",
        "rebuttal":"Exceção, condição ou objeção que limita a conclusão."
    }
    order = list(TOULMIN_LABELS)
    for row in range(0, 6, 2):
        cols = st.columns(2)
        for col, component in zip(cols, order[row:row+2]):
            items = [a for a in arguments if a.toulmin_component == component]
            with col:
                st.markdown(f"<div style='border-left:6px solid {component_color(component)};padding:9px 13px;background:rgba(128,128,128,.08)'><b>{TOULMIN_LABELS[component]}</b><br><small>{descriptions[component]}</small></div>", unsafe_allow_html=True)
                if not items: st.caption("Nenhum elemento cadastrado.")
                for a in items:
                    with st.container(border=True):
                        st.markdown(f"**{a.id}** · {a.text}")
                        if a.author: st.caption(f"Autor: {a.author}")
                        if a.qualifier: st.caption(f"Qualificador: {a.qualifier}")
    st.divider()
    st.markdown("**Importante:** componente Toulmin e tipo de relação são classificações diferentes. Por exemplo, um nó pode ser `rebuttal`, enquanto sua aresta para a conclusão pode ser `attacks`.")

with tabs[2]:
    st.subheader("Catálogo de argumentos")
    st.dataframe([{"ID":a.id,"Elemento Toulmin":TOULMIN_LABELS.get(a.toulmin_component,a.toulmin_component),"Texto":a.text,"Autor":a.author,"Posição":a.stance,"Qualificador":a.qualifier} for a in arguments], use_container_width=True, hide_index=True)

with tabs[3]:
    st.subheader("Relações entre argumentos")
    rows = [{"Origem":r.source,"Destino":r.target,"Tipo":r.relation_type} for r in relations]
    if rows: st.dataframe(rows, use_container_width=True, hide_index=True)
    else: st.info("Nenhuma relação cadastrada.")

with tabs[4]:
    st.subheader("Indicadores estruturais")
    st.caption("As métricas descrevem a topologia da rede. Elas não avaliam automaticamente a verdade, relevância ou validade lógica dos argumentos.")
    left, right = st.columns(2)
    with left:
        st.markdown("**Grau de entrada**")
        st.dataframe([{"Argumento":k,"Relações recebidas":v} for k,v in metrics["in_degree"].items()], use_container_width=True, hide_index=True)
        st.markdown("**Centralidade de grau**")
        st.dataframe([{"Argumento":k,"Centralidade":round(v,3)} for k,v in metrics["degree_centrality"].items()], use_container_width=True, hide_index=True)
    with right:
        st.markdown("**Grau de saída**")
        st.dataframe([{"Argumento":k,"Relações enviadas":v} for k,v in metrics["out_degree"].items()], use_container_width=True, hide_index=True)
        st.markdown("**Argumentos isolados**")
        st.write(", ".join(metrics["isolated_arguments"]) if metrics["isolated_arguments"] else "Nenhum")
        st.markdown("**Distribuição dos componentes**")
        st.json(metrics["component_counts"])
