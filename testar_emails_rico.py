"""
Script de diagnóstico e processamento de emails da Rico
Execute para verificar e processar emails automaticamente
"""
from tools.google_integration import GoogleIntegrationTools
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


def diagnosticar():
    """Executa diagnóstico para encontrar emails"""
    console.print(Panel("🔍 Diagnóstico de Emails da Rico", style="bold blue"))

    tools = GoogleIntegrationTools()

    # Verificar conexão primeiro
    console.print("\n[yellow]1. Verificando conexão com Google APIs...[/yellow]")
    conexao = tools.verificar_conexao()

    if conexao.get("status") == "erro":
        console.print(f"[red]❌ Erro de conexão: {conexao.get('erro', conexao.get('mensagem'))}[/red]")
        return False

    console.print(f"[green]✅ Gmail: {conexao.get('gmail')}[/green]")
    console.print(f"[green]✅ Drive: {conexao.get('drive')}[/green]")
    console.print(f"[green]✅ Sheets: {conexao.get('sheets')}[/green]")

    # Executar diagnóstico
    console.print("\n[yellow]2. Testando diferentes queries de busca...[/yellow]\n")
    diagnostico = tools.diagnosticar_emails_rico()

    if diagnostico.get("status") == "erro":
        console.print(f"[red]❌ Erro no diagnóstico: {diagnostico.get('erro')}[/red]")
        return False

    # Mostrar resultados em tabela
    table = Table(title="Resultados dos Testes")
    table.add_column("Descrição", style="cyan")
    table.add_column("Encontrados", justify="right")
    table.add_column("Exemplo", style="green")

    for teste in diagnostico.get("testes", []):
        exemplo = ""
        if "exemplo" in teste:
            exemplo = f"{teste['exemplo'].get('de', '')[:40]}..."

        status = "✅" if teste["encontrados"] > 0 else "❌"
        table.add_row(
            teste["descricao"],
            f"{status} {teste['encontrados']}",
            exemplo
        )

    console.print(table)

    # Resumo
    resumo = diagnostico.get("resumo", {})
    if resumo.get("emails_rico_encontrados"):
        console.print(f"\n[green]✅ {resumo.get('recomendacao')}[/green]")
        return True
    else:
        console.print(f"\n[red]❌ {resumo.get('recomendacao')}[/red]")
        return False


def executar_fluxo_completo():
    """Executa o fluxo completo de processamento"""
    console.print(Panel("⚙️ Executando Fluxo Completo da Rico", style="bold green"))

    tools = GoogleIntegrationTools()

    console.print("\n[yellow]Processando emails da Rico...[/yellow]")
    console.print("[dim]1. Buscando emails com anexos PDF[/dim]")
    console.print("[dim]2. Enviando PDFs para o Google Drive[/dim]")
    console.print("[dim]3. Extraindo negociações dos PDFs[/dim]")
    console.print("[dim]4. Registrando na planilha[/dim]")
    console.print("[dim]5. Marcando emails como lidos[/dim]\n")

    resultado = tools.executar_fluxo_completo_rico()

    if "erro" in resultado:
        console.print(f"[red]❌ Erro: {resultado['erro']}[/red]")
        return

    # Mostrar etapas
    console.print("[bold]Progresso:[/bold]")
    for etapa in resultado.get("etapas", []):
        console.print(f"  {etapa}")

    # Resumo final
    resumo = resultado.get("resumo", {})
    console.print("\n" + "=" * 50)
    console.print(Panel(f"""
[bold]📊 RESUMO DO PROCESSAMENTO[/bold]

📧 Emails processados: [cyan]{resumo.get('emails_processados', 0)}[/cyan]
📄 PDFs enviados ao Drive: [cyan]{resumo.get('pdfs_enviados_drive', 0)}[/cyan]
📊 PDFs com negociações: [cyan]{resumo.get('pdfs_processados', 0)}[/cyan]
📝 Negociações na planilha: [cyan]{resumo.get('negociacoes_registradas', 0)}[/cyan]
✅ Emails marcados como lidos: [cyan]{resumo.get('emails_marcados_lidos', 0)}[/cyan]
    """, title="Resultado", border_style="green"))

    if resumo.get("erros"):
        console.print(f"\n[yellow]⚠️ {len(resumo['erros'])} erro(s) encontrado(s):[/yellow]")
        for erro in resumo["erros"][:5]:
            console.print(f"  - {erro}")


def main():
    console.print(Panel("""
🏦 [bold]Processador de Emails da Rico - Caixa Forte[/bold]

Escolha uma opção:
[1] Diagnóstico - Verificar se emails estão sendo encontrados
[2] Processar - Executar fluxo completo (emails → drive → planilha)
[3] Ambos - Diagnóstico + Processamento
    """, style="bold blue"))

    opcao = console.input("\n[bold cyan]Opção (1/2/3):[/bold cyan] ").strip()

    if opcao == "1":
        diagnosticar()
    elif opcao == "2":
        executar_fluxo_completo()
    elif opcao == "3":
        if diagnosticar():
            console.print("\n")
            executar_fluxo_completo()
    else:
        console.print("[yellow]Opção inválida. Executando diagnóstico...[/yellow]\n")
        diagnosticar()


if __name__ == "__main__":
    main()
