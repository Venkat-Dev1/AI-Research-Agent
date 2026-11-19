import re

from Agents import build_scraper_agent, build_search_agent, writer_chain, critic_chain

URL_PATTERN = re.compile(r"https?://[^\s|)\]>\"']+")


def collect_urls(messages) -> list[str]:
    """Collect unique URLs from every message (including raw tool output) of an agent run."""
    urls: list[str] = []
    for m in messages:
        text = m.content if isinstance(m.content, str) else str(m.content)
        for u in URL_PATTERN.findall(text):
            u = u.rstrip(".,;")
            if u not in urls:
                urls.append(u)
    return urls


def run_research_pipeline(topic: str) -> dict:
    state = {}
    # Step 1 – Search Agent
    print("\n" + "=" * 50)
    print("Step 1 : Search Agent working ")
    print("=" * 50 + "\n")

    search_agent = build_search_agent()
    search_agent_response = search_agent.invoke({
        "messages": [("user", f"Find recent, reliable and detailed information about the {topic}")]
    })
    state["search_agent_response"] = search_agent_response["messages"][-1].content
    # URLs come from the raw tool output, so they survive even if the model drops them
    state["urls"] = collect_urls(search_agent_response["messages"])
    print("Search Results : \n", state["search_agent_response"])

    # Step 2 – Scraper Agent (Reader Ability)
    print("\n" + "=" * 50)
    print("Step 2 : Reader Agent is Scraping top results from the search results ")
    print("=" * 50 + "\n")

    first_url = state["urls"][0] if state["urls"] else ""

    if not first_url:
        print("\n No URL found in search results; skipping scraper step.\n")
        state["Scrapped_content"] = ""
    else:
        reader_agent = build_scraper_agent()
        reader_result = reader_agent.invoke({
            "messages": [("user", first_url)]
        })
        # The web_scraper tool returns the scraped text as the content of the last message
        state["Scrapped_content"] = reader_result["messages"][-1].content

    print("\n Scrapped Content \n", state["Scrapped_content"])

    # Step 3 – Writer chain
    print("\n" + "=" * 50)
    print("Step 3 : Writer is drafting the report...")
    print("=" * 50 + "\n")

    sources_block = "\n".join(f"- {u}" for u in state["urls"])
    search_results_combine = (
        f"Search Results :\n {state['search_agent_response']}\n\n"
        f"Source URLs :\n{sources_block}\n\n"
        f"Detailed Scrapped Content :\n{state['Scrapped_content']}"
    )
    state["report"] = writer_chain.invoke({
        "topic": topic,
        "research": search_results_combine,
    })
    print("\n Final Report \n", state["report"])

    # Step 4 – Critic report with error handling
    print("\n" + "=" * 50)
    print("Step 4 : Producing the Score for writer generated report...")
    print("=" * 50 + "\n")
    try:
        feedback = critic_chain.invoke({"report": state["report"]})
        if not feedback.strip():
            # one retry, in case the first attempt used the whole budget on reasoning
            feedback = critic_chain.invoke({"report": state["report"]})
        state["feedback"] = feedback or "Critic failed: model returned an empty response."
    except Exception as e:
        state["feedback"] = f"Critic failed: {e}"
    return state


if __name__ == "__main__":
    topic = input("\n Enter the Research topic :")
    run_research_pipeline(topic)