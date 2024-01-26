# module specific business logic
import json
import traceback

from src.articles.models import ArticleParameter, Article
from src.config import settings
from src.documents.schemas import ParserEnum
from src.documents.utils import rag_topic_to_answer, chat_to_answer
from src.utils import init_db
import logging

async def article_create_one(keyword: str, article_option_name: str, article_parameter: ArticleParameter, tries: int = 6):
    for i in range(tries):
        try:
            logging.warning("Start generating article - " + keyword)

            # 大纲生成，大纲必须规范结果为合适的json
            outline_prompt = article_parameter.outline_prompt + """\nFinally, output the outline by JSON object structured like:{{"title": "", "sections": [{{"heading": "", "content":""}}]}}"""
            outline = await rag_topic_to_answer(keyword,
                                                outline_prompt,
                                                article_parameter.outline_model,
                                                article_parameter.outline_retriever_type,
                                                ParserEnum.json,
                                                article_parameter.outline_fetch_k,
                                                article_parameter.outline_k)
            content = "# " + outline.get("answer").get("title")
            outline_context_dict = [{"page_content": doc.page_content, "metadata": doc.metadata} for doc in outline.get("context")]

            # 内容生成
            outline_sections = outline.get("answer").get("sections")
            paragraph_contexts = []
            for section in outline_sections:
                if section == outline_sections[0]:
                    human_1="I will provide you with the blog outline in json format. Write an Introduction of the article within 100 words based on the outline. Output content only.\n\noutline:\n" + json.dumps(
                            outline.get("answer")) + "\n\nIntroduction topic:\n" + section.get("heading")
                    introduction = await chat_to_answer(human_1=human_1)
                    content += "\n\n## " + section.get("heading") + "\n\n" + introduction
                elif section == outline_sections[-1] and section.get("heading").startswith("Conclusion"):
                    human_1="I will provide you with the blog outline in json format. Write an Conclusion of the article within 100 words based on the outline. Output content only.\n\noutline:\n" + json.dumps(
                            outline.get("answer"))
                    conclusion = await chat_to_answer(human_1=human_1)
                    content += "\n\n## " + section.get("heading") + "\n\n" + conclusion
                else:
                    topic = "## " + section.get("heading") + "\n\n" + section.get("content")
                    p_prompt = article_parameter.paragraph_prompt + """\nFinally, content must be output in markdown format."""
                    p = await rag_topic_to_answer(topic,
                                                  p_prompt,
                                                  article_parameter.paragraph_model,
                                                  article_parameter.paragraph_retriever_type,
                                                  ParserEnum.str,
                                                  article_parameter.paragraph_fetch_k,
                                                  article_parameter.paragraph_k)
                    content += "\n\n" + p.get("answer")
                    paragraph_contexts += p.get("context")
            paragraph_context_dict = [{"page_content": doc.page_content, "metadata": doc.metadata} for doc in paragraph_contexts]

            # 生成的文章存入数据库
            await init_db(settings.db_name, [Article])
            article = Article(keyword=keyword,
                              article_option_name=article_option_name,
                              article_parameter=article_parameter,
                              content=content,
                              outline=outline.get("answer"),
                              outline_context=outline_context_dict,
                              paragraph_context=paragraph_context_dict)
            await article.insert()
            logging.warning("Article generated and stored successfully - " + keyword)

            return article
        except Exception as e:
            logging.error(str(e))
            traceback.print_exc(file=open(settings.log_file,"a"))
            if i == tries - 1:
                logging.error("Article generation failed - " + keyword)

