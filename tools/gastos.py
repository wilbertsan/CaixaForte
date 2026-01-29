"""
Tools para controle de gastos pessoais e orçamento
"""
from typing import Optional, List, Dict
from datetime import datetime
import json
import os


class GastosTools:
    """Ferramentas para controle de gastos pessoais"""

    def __init__(self, arquivo_dados: str = "dados_financeiros.json"):
        self.arquivo_dados = arquivo_dados
        self.dados = self._carregar_dados()

    def _carregar_dados(self) -> dict:
        """Carrega dados do arquivo JSON"""
        if os.path.exists(self.arquivo_dados):
            try:
                with open(self.arquivo_dados, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {
            "gastos": [],
            "receitas": [],
            "orcamento": {},
            "categorias_gasto": [
                "Alimentacao", "Moradia", "Transporte", "Saude",
                "Educacao", "Lazer", "Vestuario", "Outros"
            ],
            "categorias_receita": [
                "Salario", "Freelance", "Investimentos", "Outros"
            ]
        }

    def _salvar_dados(self):
        """Salva dados no arquivo JSON"""
        with open(self.arquivo_dados, 'w', encoding='utf-8') as f:
            json.dump(self.dados, f, ensure_ascii=False, indent=2)

    def registrar_gasto(self, valor: float, categoria: str, descricao: str,
                        data: Optional[str] = None) -> dict:
        """
        Registra um novo gasto.

        Args:
            valor: Valor do gasto
            categoria: Categoria do gasto
            descricao: Descrição do gasto
            data: Data no formato YYYY-MM-DD (opcional, usa hoje se não informado)

        Returns:
            Confirmação do registro
        """
        if data is None:
            data = datetime.now().strftime("%Y-%m-%d")

        gasto = {
            "id": len(self.dados["gastos"]) + 1,
            "valor": valor,
            "categoria": categoria,
            "descricao": descricao,
            "data": data,
            "criado_em": datetime.now().isoformat()
        }

        self.dados["gastos"].append(gasto)
        self._salvar_dados()

        return {
            "status": "sucesso",
            "mensagem": f"Gasto de R$ {valor:.2f} registrado na categoria {categoria}",
            "gasto": gasto
        }

    def registrar_receita(self, valor: float, categoria: str, descricao: str,
                          data: Optional[str] = None) -> dict:
        """
        Registra uma nova receita.

        Args:
            valor: Valor da receita
            categoria: Categoria da receita
            descricao: Descrição da receita
            data: Data no formato YYYY-MM-DD

        Returns:
            Confirmação do registro
        """
        if data is None:
            data = datetime.now().strftime("%Y-%m-%d")

        receita = {
            "id": len(self.dados["receitas"]) + 1,
            "valor": valor,
            "categoria": categoria,
            "descricao": descricao,
            "data": data,
            "criado_em": datetime.now().isoformat()
        }

        self.dados["receitas"].append(receita)
        self._salvar_dados()

        return {
            "status": "sucesso",
            "mensagem": f"Receita de R$ {valor:.2f} registrada na categoria {categoria}",
            "receita": receita
        }

    def definir_orcamento(self, categoria: str, limite_mensal: float) -> dict:
        """
        Define orçamento mensal para uma categoria.

        Args:
            categoria: Categoria de gasto
            limite_mensal: Limite mensal em reais

        Returns:
            Confirmação do orçamento
        """
        self.dados["orcamento"][categoria] = limite_mensal
        self._salvar_dados()

        return {
            "status": "sucesso",
            "mensagem": f"Orçamento de R$ {limite_mensal:.2f} definido para {categoria}",
            "orcamento_atual": self.dados["orcamento"]
        }

    def resumo_mensal(self, mes: Optional[int] = None, ano: Optional[int] = None) -> dict:
        """
        Gera resumo financeiro do mês.

        Args:
            mes: Mês (1-12), usa mês atual se não informado
            ano: Ano, usa ano atual se não informado

        Returns:
            Resumo financeiro do mês
        """
        if mes is None:
            mes = datetime.now().month
        if ano is None:
            ano = datetime.now().year

        # Filtrar gastos do mês
        gastos_mes = [
            g for g in self.dados["gastos"]
            if g["data"].startswith(f"{ano}-{mes:02d}")
        ]

        # Filtrar receitas do mês
        receitas_mes = [
            r for r in self.dados["receitas"]
            if r["data"].startswith(f"{ano}-{mes:02d}")
        ]

        # Calcular totais por categoria
        gastos_por_categoria = {}
        for g in gastos_mes:
            cat = g["categoria"]
            gastos_por_categoria[cat] = gastos_por_categoria.get(cat, 0) + g["valor"]

        receitas_por_categoria = {}
        for r in receitas_mes:
            cat = r["categoria"]
            receitas_por_categoria[cat] = receitas_por_categoria.get(cat, 0) + r["valor"]

        total_gastos = sum(g["valor"] for g in gastos_mes)
        total_receitas = sum(r["valor"] for r in receitas_mes)
        saldo = total_receitas - total_gastos

        # Verificar orçamento
        alertas_orcamento = []
        for cat, limite in self.dados["orcamento"].items():
            gasto_cat = gastos_por_categoria.get(cat, 0)
            if gasto_cat > limite:
                alertas_orcamento.append({
                    "categoria": cat,
                    "limite": limite,
                    "gasto": gasto_cat,
                    "excedente": gasto_cat - limite
                })
            elif gasto_cat > limite * 0.8:
                alertas_orcamento.append({
                    "categoria": cat,
                    "limite": limite,
                    "gasto": gasto_cat,
                    "alerta": "Próximo do limite (>80%)"
                })

        return {
            "periodo": f"{mes:02d}/{ano}",
            "total_receitas": round(total_receitas, 2),
            "total_gastos": round(total_gastos, 2),
            "saldo": round(saldo, 2),
            "gastos_por_categoria": {k: round(v, 2) for k, v in gastos_por_categoria.items()},
            "receitas_por_categoria": {k: round(v, 2) for k, v in receitas_por_categoria.items()},
            "alertas_orcamento": alertas_orcamento,
            "taxa_poupanca": round((saldo / total_receitas * 100), 2) if total_receitas > 0 else 0
        }

    def listar_gastos(self, categoria: Optional[str] = None,
                      limite: int = 10) -> dict:
        """
        Lista os últimos gastos.

        Args:
            categoria: Filtrar por categoria (opcional)
            limite: Número máximo de registros

        Returns:
            Lista de gastos
        """
        gastos = self.dados["gastos"]

        if categoria:
            gastos = [g for g in gastos if g["categoria"] == categoria]

        # Ordenar por data (mais recente primeiro)
        gastos = sorted(gastos, key=lambda x: x["data"], reverse=True)[:limite]

        return {
            "total_registros": len(gastos),
            "gastos": gastos
        }

    def analisar_gastos(self) -> dict:
        """
        Analisa padrões de gastos e dá sugestões.

        Returns:
            Análise e sugestões
        """
        if not self.dados["gastos"]:
            return {"mensagem": "Nenhum gasto registrado ainda"}

        # Gastos dos últimos 3 meses
        hoje = datetime.now()
        gastos_recentes = []
        for g in self.dados["gastos"]:
            data_gasto = datetime.strptime(g["data"], "%Y-%m-%d")
            diff = (hoje - data_gasto).days
            if diff <= 90:
                gastos_recentes.append(g)

        if not gastos_recentes:
            return {"mensagem": "Nenhum gasto nos últimos 3 meses"}

        # Análise por categoria
        por_categoria = {}
        for g in gastos_recentes:
            cat = g["categoria"]
            if cat not in por_categoria:
                por_categoria[cat] = []
            por_categoria[cat].append(g["valor"])

        analise = {}
        for cat, valores in por_categoria.items():
            analise[cat] = {
                "total": round(sum(valores), 2),
                "media": round(sum(valores) / len(valores), 2),
                "quantidade": len(valores),
                "maior_gasto": round(max(valores), 2),
                "menor_gasto": round(min(valores), 2)
            }

        # Identificar maior categoria
        maior_cat = max(analise.items(), key=lambda x: x[1]["total"])

        sugestoes = []
        total_gastos = sum(a["total"] for a in analise.values())

        for cat, dados in analise.items():
            percentual = (dados["total"] / total_gastos) * 100
            if percentual > 30:
                sugestoes.append(
                    f"{cat} representa {percentual:.1f}% dos seus gastos. "
                    "Considere revisar esta categoria."
                )

        return {
            "periodo_analise": "Últimos 3 meses",
            "total_gasto": round(total_gastos, 2),
            "media_mensal": round(total_gastos / 3, 2),
            "maior_categoria": {
                "nome": maior_cat[0],
                "total": maior_cat[1]["total"]
            },
            "analise_por_categoria": analise,
            "sugestoes": sugestoes
        }

    def get_categorias(self) -> dict:
        """
        Retorna as categorias disponíveis.

        Returns:
            Categorias de gastos e receitas
        """
        return {
            "categorias_gasto": self.dados["categorias_gasto"],
            "categorias_receita": self.dados["categorias_receita"]
        }
