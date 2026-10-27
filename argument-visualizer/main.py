
import streamlit as st

from streamlit_agraph import agraph, Node, Edge, Config

from src.data_loader import load_data
from src.graph_builder import build_graph
from src.analyzer import analyze_graph


# --------------------------------------------------
# 1. Configuração da página
# --------------------------------------------------

st.set_page_config(
    page_title="Argument Visualizer",
    page_icon="🔎",
    layout="wide",
)

st.title("🔎 Argument Visualizer")
st.write(
    "Explore uma rede de argumentos. Clique em um nó "
    "para consultar o argumento completo."
)


# --------------------------------------------------
# 2. Upload do arquivo
# --------------------------------------------------

uploaded_file = st.file_uploader(
    "Enviar arquivo JSON",
    type=["json"],
)


# --------------------------------------------------
# 3. Processamento
# --------------------------------------------------

if uploaded_file is not None:
    try:
        metadata, arguments, relations = load_data(uploaded_file)

        graph = build_graph(arguments, relations)
        metrics = analyze_graph(graph)

        st.subheader(
            metadata.get("title", "Análise de argumentos")
        )

        if metadata.get("source"):
            st.caption(f"Fonte: {metadata['source']}")

        col1, col2, col3 = st.columns(3)

        col1.metric("Argumentos", metrics["arguments"])
        col2.metric("Relações", metrics["relations"])
        col3.metric("Densidade", f"{metrics['density']:.3f}")

        # --------------------------------------------------
        # 4. Abas
        # --------------------------------------------------

        tab_graph, tab_arguments, tab_relations, tab_metrics = st.tabs(
            [
                "Visualização interativa",
                "Argumentos",
                "Relações",
                "Estatísticas",
            ]
        )

        # --------------------------------------------------
        # 5. Grafo interativo
        # --------------------------------------------------

        with tab_graph:
            st.subheader("Rede de argumentos")

            st.caption(
                "Arraste os nós para reorganizar a rede. "
                "Use o zoom para explorar e clique em um nó "
                "para ler seu conteúdo."
            )

            nodes = []

            for argument in arguments:
                stance = argument.stance.lower()

                if stance == "pro":
                    node_color = "#9BD7A5"
                elif stance == "con":
                    node_color = "#F2A0A0"
                else:
                    node_color = "#A8C7FA"

                nodes.append(
                    Node(
                        id=argument.id,
                        label=argument.id,
                        size=25,
                        color=node_color,
                        shape="dot",
                    )
                )

            edges = []

            for relation in relations:
                if relation.relation_type.lower() in (
                    "attacks",
                    "rebuts",
                    "attacks",
                ):
                    edge_color = "#D64545"
                else:
                    edge_color = "#479B68"

                edges.append(
                    Edge(
                        source=relation.source,
                        target=relation.target,
                        label=relation.relation_type,
                        color=edge_color,
                    )
                )

            config = Config(
                width="100%",
                height=650,
                directed=True,
                physics=True,
                hierarchical=False,
                nodeHighlightBehavior=True,
                highlightColor="#FFD166",
                collapsible=False,
            )

            selected_node = agraph(
                nodes=nodes,
                edges=edges,
                config=config,
            )

            # O componente pode retornar o ID do nó selecionado.
            selected_id = None

            if isinstance(selected_node, str):
                selected_id = selected_node
            elif isinstance(selected_node, dict):
                selected_id = selected_node.get("id")

            # --------------------------------------------------
            # 6. Mostrar conteúdo somente após clicar
            # --------------------------------------------------

            if selected_id and selected_id in graph.nodes:
                attributes = graph.nodes[selected_id]

                st.divider()
                st.subheader(f"Argumento {selected_id}")

                st.markdown("**Texto apresentado pelo usuário**")
                st.write(
                    attributes.get("text", "Texto não disponível.")
                )

                st.write(
                    f"**Autor:** "
                    f"{attributes.get('author') or 'Não informado'}"
                )

                st.write(
                    f"**Tipo:** "
                    f"{attributes.get('argument_type') or 'Não informado'}"
                )

                st.write(
                    f"**Posicionamento:** "
                    f"{attributes.get('stance') or 'Não informado'}"
                )

                st.divider()
                st.subheader("Conexões do argumento")

                incoming = list(
                    graph.in_edges(selected_id, data=True)
                )
                outgoing = list(
                    graph.out_edges(selected_id, data=True)
                )

                st.markdown("**Argumentos que apontam para este nó**")

                if incoming:
                    for source, target, data in incoming:
                        st.write(
                            f"{source} → {target} "
                            f"({data.get('relation_type', 'sem tipo')})"
                        )
                else:
                    st.write("Nenhuma relação recebida.")

                st.markdown("**Argumentos para os quais este nó aponta**")

                if outgoing:
                    for source, target, data in outgoing:
                        st.write(
                            f"{source} → {target} "
                            f"({data.get('relation_type', 'sem tipo')})"
                        )
                else:
                    st.write("Nenhuma relação enviada.")

            else:
                st.info(
                    "Clique em um argumento no grafo para "
                    "visualizar seu texto e suas conexões."
                )

        # --------------------------------------------------
        # 7. Tabela de argumentos
        # --------------------------------------------------

        with tab_arguments:
            st.subheader("Argumentos")

            st.dataframe(
                [
                    {
                        "ID": argument.id,
                        "Texto": argument.text,
                        "Autor": argument.author,
                        "Tipo": argument.argument_type,
                        "Posicionamento": argument.stance,
                    }
                    for argument in arguments
                ],
                use_container_width=True,
                hide_index=True,
            )

        # --------------------------------------------------
        # 8. Tabela de relações
        # --------------------------------------------------

        with tab_relations:
            st.subheader("Relações")

            relation_rows = [
                {
                    "Origem": relation.source,
                    "Destino": relation.target,
                    "Tipo": relation.relation_type,
                }
                for relation in relations
            ]

            if relation_rows:
                st.dataframe(
                    relation_rows,
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.info("Nenhuma relação encontrada.")

        # --------------------------------------------------
        # 9. Estatísticas
        # --------------------------------------------------

        with tab_metrics:
            st.subheader("Estatísticas da rede")

            st.metric("Total de argumentos", metrics["arguments"])
            st.metric("Total de relações", metrics["relations"])
            st.metric("Densidade", f"{metrics['density']:.3f}")

            st.write("**Argumentos isolados**")

            if metrics["isolated_arguments"]:
                st.write(", ".join(metrics["isolated_arguments"]))
            else:
                st.write("Nenhum argumento isolado.")

            st.write("**Relações recebidas por argumento**")
            st.json(metrics["in_degree"])

            st.write("**Relações enviadas por argumento**")
            st.json(metrics["out_degree"])

    except (ValueError, KeyError, TypeError) as error:
        st.error(f"Não foi possível processar os dados: {error}")

    except Exception as error:
        st.error(f"Ocorreu um erro inesperado: {error}")

else:
    st.info("Envie um arquivo JSON para começar.")

    st.markdown(
        """
        O arquivo deve conter:
        - `arguments`: lista de argumentos;
        - `relations`: lista de relações;
        - `metadata`: informações opcionais.
        """
    )
