from src.services.ai.schemas import SummarySchema



class SummaryParser:


    def parse(
        self,
        data: dict
    ) -> dict:


        try:

            result = SummarySchema(
                **data
            )


            return result.model_dump()


        except Exception as e:


            print(
                "Schema validation error:",
                e
            )


            return {
                "overview": "",
                "key_points": [],
                "important_terms": [],
                "tools": [],
                "resources": [],
                "final_takeaway": ""
            }