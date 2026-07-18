import json
import logging

from src.services.ai.chunker import TranscriptChunker
from src.services.ai.openrouter_client import OpenRouterClient
from src.services.ai.parser import SummaryParser


logger = logging.getLogger(
    "youtube_summarizer"
)


class MapReduceSummarizer:
    """
    Summarize long transcripts using Map-Reduce strategy.
    """

    def __init__(self):

        self.chunker = TranscriptChunker()

        self.client = OpenRouterClient()

        self.parser = SummaryParser()



    def summarize(
        self,
        transcript: str,
        language: str = "Persian",
        summary_type: str = "detailed"
    ) -> dict:


        # ==========================
        # MAP PHASE
        # ==========================

        chunks = self.chunker.split(
            transcript
        )


        if not chunks:

            return {

                "overview": "متنی برای خلاصه‌سازی وجود ندارد.",

                "key_points": [],

                "important_terms": [],

                "tools": [],

                "resources": [],

                "final_takeaway": ""

            }



        partial_summaries = []



        for index, chunk in enumerate(chunks):


            logger.info(

                f"Summarizing chunk {index + 1}/{len(chunks)}"

            )


            try:


                summary = self.client.summarize_json(


                    system_prompt="""

You are a professional educational YouTube summarizer.

Analyze ONLY the provided transcript section.

Do not invent information.

Return ONLY valid JSON.

Format:

{
"summary":"",
"key_points":[],
"important_terms":[],
"tools":[],
"resources":[]
}

""",


                    user_prompt=f"""

Language:

{language}


Summary style:

{summary_type}


Transcript section:

{chunk}

"""

                )



                logger.info(

                    f"Chunk {index + 1} result: {summary}"

                )



                if summary:

                    partial_summaries.append(
                        summary
                    )

                else:

                    logger.warning(

                        f"Chunk {index + 1} returned empty result"

                    )



            except Exception as e:


                logger.exception(

                    f"Chunk {index + 1} failed: {e}"

                )



                continue





        # ==========================
        # CHECK MAP RESULT
        # ==========================


        if not partial_summaries:


            return {

                "overview": "AI نتوانست بخش‌های ویدیو را خلاصه کند.",

                "key_points": [],

                "important_terms": [],

                "tools": [],

                "resources": [],

                "final_takeaway": ""

            }





        # ==========================
        # PREPARE REDUCE INPUT
        # ==========================


        combined = "\n\n".join(

            [

                f"""
SECTION {i + 1}

{json.dumps(
    item,
    ensure_ascii=False
)}

"""

                for i, item in enumerate(partial_summaries)

            ]

        )





        # ==========================
        # REDUCE PHASE
        # ==========================


        try:


            final_result = self.client.summarize_json(



                system_prompt="""

You are an expert educational content editor.

Combine the summaries into one complete educational summary.

Rules:

- Use only provided information.
- Do not invent facts.
- Return ONLY valid JSON.

""",



                user_prompt=f"""

Language:

{language}


Summary type:

{summary_type}



Required JSON:

{{
"overview":"",
"key_points":[],
"important_terms":[],
"tools":[],
"resources":[],
"final_takeaway":""
}}



Input summaries:

{combined}

"""

            )



            logger.info(

                f"FINAL AI RESULT: {final_result}"

            )



        except Exception as e:


            logger.exception(

                f"Reduce failed: {e}"

            )


            return {

                "overview": "خطا در تولید خلاصه نهایی.",

                "key_points": [],

                "important_terms": [],

                "tools": [],

                "resources": [],

                "final_takeaway": ""

            }





        # ==========================
        # PARSE RESULT
        # ==========================


        if not final_result:


            return {

                "overview": "خروجی AI خالی بود.",

                "key_points": [],

                "important_terms": [],

                "tools": [],

                "resources": [],

                "final_takeaway": ""

            }




        parsed = self.parser.parse(

            final_result

        )



        if not parsed:


            logger.error(

                "Parser returned empty result"

            )


            return {

                "overview": "خلاصه تولید نشد.",

                "key_points": [],

                "important_terms": [],

                "tools": [],

                "resources": [],

                "final_takeaway": ""

            }



        return parsed