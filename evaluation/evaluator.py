
from .rubrics import CITATION_EVAL_PROMPT, SPECIFICITY_PROMPT, CATEGORY_EVAL_PROMPT, RELEVANCE_EVAL_PROMPT, PLAN_JUDGE_PROMPT_PERSONALIZATION, PLAN_CONTRADICT_QUERY, PLAN_CATEGORY_QUERY
from data import AtomicInference, HighLevelInference, PaperSnippet, UserConstitution, Plan
from enums import ConstitutionCategory, CONSTITUTION_DEFINITION_RUBRIC, PERSONALIZATION_STRATEGY_RUBRIC, PERSONALIZATION_FRAMEWORK_RUBRIC
from .metrics import ConstitutionEvalRun, PlanMetrics, ConstitutionMetrics, InferenceMetric, PlanEvalRun
from llms.model_factory import ModelFactory
import tqdm

"""Handles all evaluations for the constitutions"""
class ProfileEvaluator:

    def __init__(self, judge_model_name, judge_model_type):
        self.judge = ModelFactory().get_model(model_type=judge_model_type, model_name=judge_model_name, temp=0.0)

    """How specific are the inferences in isolation"""
    def score_specificity_batch(self, inferences: list[AtomicInference | HighLevelInference]) -> list[int]:
        inf_prompts = [SPECIFICITY_PROMPT.format(inference=inf.text) for inf in inferences]
        outputs = []
        for inf_prompt in tqdm.tqdm(inf_prompts):
            outputs.append(self.judge.generate_json(inf_prompt.strip(), target_json={'output': 1}))
        return [int(o['output']) for o in outputs]

    """Are the atomic inferences relevant?"""
    def score_relevance_batch(self, inferences: list[HighLevelInference]):
        out_data = []
        for hli in tqdm.tqdm(inferences):
            cite_relevance = []
            total = len(hli.sources)
            paper_titles = set()
            num_relevant = 0
            for ali in hli.sources:
                inf_prompt = RELEVANCE_EVAL_PROMPT.format(paper_text='\n'.join([t.text for t in ali.sources]), hli=hli.text).strip()
                output = self.judge.generate_json(prompt=inf_prompt, target_json={'output': ''})
                num_relevant += int(output['output'] == 'Relevant')
                cite_relevance.append(int(output['output'] == 'Relevant'))
                try:
                    paper_titles.add(ali.sources[0].source_paper.title)
                except Exception as e:
                    print('error:', str(e))
            out_data.append({'total_papers': total, 'unique_papers': len(paper_titles), 'relevant_papers': num_relevant, 'cite_relevance': cite_relevance})
        return out_data
    
    """How accurate/faithful are the inferences relative to input contexts"""
    def score_accuracy_batch(self, inferences: list[AtomicInference | HighLevelInference], evidences: list[list[PaperSnippet] | list[AtomicInference]]) -> list[int]:
        source_strs = ['\n'.join(['\n'.join(f'<reference {paper_idx+1}>\n' + p.text + f'\n</reference {paper_idx+1}>' for paper_idx, p in enumerate(context.sources)) for context in evidence]) for evidence in evidences]
        inf_prompts = [CITATION_EVAL_PROMPT.format(ref_excerpt=source_str, inference=inf.text) for inf, source_str in zip(inferences, source_strs)]
        outputs = []
        for inf_prompt in tqdm.tqdm(inf_prompts):
            outputs.append(self.judge.generate_json(inf_prompt.strip(), target_json={'output': ''}))
        return [int(o['output'] != 'Contradictory') for o in outputs]
    
    """Does the inference fall under the right category?"""
    def score_categorization_batch(self, inferences: list[AtomicInference | HighLevelInference], categories: list[ConstitutionCategory]) -> list[int]:
        inf_prompts = [CATEGORY_EVAL_PROMPT.format(inference=inf.text, category=category.value.title(), definition=CONSTITUTION_DEFINITION_RUBRIC[category].strip()) for inf, category in zip(inferences, categories)]
        outputs = []
        for inf_prompt in tqdm.tqdm(inf_prompts):
            outputs.append(self.judge.generate_json(inf_prompt.strip(), target_json={'output': ''}))
        return [int(o['output'] == 'Match') for o in outputs]
    
    """What proportion of papers did the inference cover?"""
    def score_prop_covered(self, inference: HighLevelInference | AtomicInference, num_papers: int) -> float:
        papers_seen = set()
        if type(inference) == HighLevelInference:
            for ali in inference.sources:
                for snippet in ali.sources:
                    papers_seen.add(snippet.source_paper.paper_id)
        else:
            for snippet in inference.sources:
                papers_seen.add(snippet.source_paper.paper_id)
        return (1.0 * len(papers_seen)) / num_papers
    
    def score_prop_covered_batch(self, inferences: list[HighLevelInference] | list[AtomicInference], num_papers: int) -> list[float]:
        out = []
        for inf in inferences:
            out.append(self.score_prop_covered(inference=inf, num_papers=num_papers))
        return out
    
    """How many papers did the inference cover?"""
    def score_num_covered(self, inference: HighLevelInference | AtomicInference) -> int:
        total = 0
        if type(inference) == HighLevelInference:
            for ali in inference.sources:
                total += len(ali.sources)
        else:
            total += len(inference.sources)
        return total
    
    def score_num_covered_batch(self, inferences: list[HighLevelInference] | list[AtomicInference]) -> list[int]:
        out = []
        for inf in inferences:
            out.append(self.score_num_covered(inf))
        return out

    def prepare_profile_data(self, constitutions: list[UserConstitution]):
        all_high, all_atomic = [], []
        all_ids, all_ids_high = [], []
        all_cats, all_cats_high = [], []

        for const_id, const in enumerate(constitutions):
            for cat, hlis in const.inferences.items():
                for hli in hlis:
                    all_high.append(hli)
                    for ali in hli.sources:
                        all_atomic.append(ali)
                        all_ids.append(const_id)
                        all_cats.append(cat)

                    all_ids_high.append(const_id)
                    all_cats_high.append(cat)

        return {#'atomic': {'inferences': all_atomic, 'ids': all_ids, 'categories': all_cats}, # uncomment this line if you also want to score atomic-level inferences
                'high_level': {'inferences': all_high, 'ids': all_ids_high, 'categories': all_cats_high}}

    """Turn metric data into metric objects"""
    def build_metrics(self, metric_data: dict, constitutions: list[UserConstitution]):
        const_metrics = [ConstitutionMetrics.from_constitution(constitution=const) for const in constitutions]
        # for inf_metric, const_id, cat in zip(metric_data['atomic_metrics'], metric_data['atomic_ids'], metric_data['atomic_categories']):
        #     const_metrics[const_id].insert_ali(metric=inf_metric, category=cat)
        for inf_metric, const_id, cat in zip(metric_data['high_level_metrics'], metric_data['high_level_ids'], metric_data['high_level_categories']):
            const_metrics[const_id].insert_hli(metric=inf_metric, category=cat)

        #assert all(metric.is_valid() for metric in const_metrics), "There was an error parsing the metrics"
        return const_metrics

    """Run the full evaluation"""
    def evaluate(self, user_ids: list[str], constitutions: list[UserConstitution], run_name: str, output_dir: str):
        const_data = self.prepare_profile_data(constitutions=constitutions)

        metric_data = {}
        for inf_name, inf_data in const_data.items():


            curr_metrics = [InferenceMetric.default() for _ in inf_data['ids']]
            
            if inf_name == 'high_level':
                print('Only scoring relevance for high-level inferences')
                for idx, metric in enumerate(self.score_relevance_batch(inferences=inf_data['inferences'])):
                    curr_metrics[idx].num_cites = metric['total_papers']
                    curr_metrics[idx].num_unique_cites = metric['unique_papers']
                    curr_metrics[idx].num_relevant_cites = metric['relevant_papers']
                    curr_metrics[idx].cite_relevance = metric['cite_relevance']

            # accuracy / faithfulness
            print('scoring accuracy')
            for idx, metric in enumerate(self.score_accuracy_batch(inferences=inf_data['inferences'], evidences=[inf.sources for inf in inf_data['inferences']])):
                curr_metrics[idx].source_accuracy = metric

            # categorization
            print('scoring categorization')
            for idx, metric in enumerate(self.score_categorization_batch(inferences=inf_data['inferences'], categories=inf_data['categories'])):
                curr_metrics[idx].category_accuracy = metric

            # specificity
            print('scoring specificity')
            for idx, metric in enumerate(self.score_specificity_batch(inferences=inf_data['inferences'])):
                curr_metrics[idx].specificity = metric

            metric_data[f'{inf_name}_metrics'] = curr_metrics
            metric_data[f'{inf_name}_ids'] = inf_data['ids']
            metric_data[f'{inf_name}_categories'] = inf_data['categories']

        const_metrics = self.build_metrics(metric_data=metric_data, constitutions=constitutions)
        eval_run = ConstitutionEvalRun(metrics={user_id: met for user_id, met in zip(user_ids, const_metrics)})
        eval_run.to_json(output_dir=output_dir, run_name=run_name)
 
class PersonalizedPlanEvaluator:

    def __init__(self, judge_model_name, judge_model_type):
        self.judge = ModelFactory().get_model(model_type=judge_model_type, model_name=judge_model_name, temp=0.0)

    def parse_reqs(self, reqs: list[str], query: str):
        return '\n'.join(['- ' + r.text for r in reqs])

    def score_comparison_batch_personalization(self, personalized_plans: list[Plan], normal_plans: list[Plan], constitutions: list[UserConstitution], queries: list[str]):

        metrics = []
        for query, personalized_plan, normal_plan, constitution in tqdm.tqdm(list(zip(queries, personalized_plans, normal_plans, constitutions))):
            all_scores = dict()
            for strategy in personalized_plan.requirements.keys():
                if strategy not in normal_plan.requirements:
                    print('skipping!')
                    continue
                personalized_reqs, normal_reqs = personalized_plan.requirements[strategy], normal_plan.requirements[strategy]

                inf_prompt = PLAN_JUDGE_PROMPT_PERSONALIZATION.format(profile=constitution.to_markdown(),
                                                    plan_a=self.parse_reqs(reqs=personalized_reqs, query=query),
                                                    plan_b=self.parse_reqs(reqs=normal_reqs, query=query)
                                                    )
                judgement_normal = self.judge.generate_json(prompt=inf_prompt.strip(), target_json={'output': ''})['output']

                inf_prompt_swap = PLAN_JUDGE_PROMPT_PERSONALIZATION.format(profile=constitution.to_markdown(),
                                                plan_b=self.parse_reqs(reqs=personalized_reqs, query=query),
                                                plan_a=self.parse_reqs(reqs=normal_reqs, query=query)
                                                )
                judgment_swap = self.judge.generate_json(prompt=inf_prompt_swap.strip(), target_json={'output': ''})['output']

                judgment = judgement_normal if (judgement_normal != judgment_swap) else 'Tie'
                all_scores[strategy] = (judgment, str(personalized_plan), str(normal_plan))
            metrics.append(PlanMetrics(metrics=all_scores))

        return metrics
    
    def score_comparison_batch_query(self, personalized_plans: list[Plan], normal_plans: list[Plan], constitutions: list[UserConstitution], queries: list[str]):

        metrics = []
        for query, personalized_plan, normal_plan, constitution in tqdm.tqdm(list(zip(queries, personalized_plans, normal_plans, constitutions))):
            all_scores = dict()
            for strategy in personalized_plan.requirements.keys():
                if strategy not in normal_plan.requirements:
                    print('skipping!')
                    continue
                personalized_reqs, normal_reqs = personalized_plan.requirements[strategy], normal_plan.requirements[strategy]

                out_p = []
                for req in personalized_reqs:
                    inf_prompt = PLAN_CONTRADICT_QUERY.format(query=query,
                                                        plan=req.text,
                                                        )
                    judgement_personalized = self.judge.generate_json(prompt=inf_prompt.strip(), target_json={'output': ''})
                    judgement_personalized_expl = judgement_personalized['explanation']
                    judgement_personalized = judgement_personalized['output'] == 'CONFLICT'
                    out_p.append((judgement_personalized, judgement_personalized_expl))

                out_n = []
                for req in normal_reqs:
                    inf_prompt = PLAN_CONTRADICT_QUERY.format(query=query,
                                                    plan=req.text
                                                    )
                    judgment_normal = self.judge.generate_json(prompt=inf_prompt.strip(), target_json={'output': ''})
                    judgement_normal_expl = judgment_normal['explanation']
                    judgment_normal = judgment_normal['output'] == 'CONFLICT'
                    out_n.append((judgment_normal, judgement_normal_expl))


                all_scores[strategy] = ((out_p, out_n), str(personalized_plan), str(normal_plan))
            metrics.append(PlanMetrics(metrics=all_scores))

        return metrics

    def score_category_batch(self, personalized_plans: list[Plan], normal_plans: list[Plan], constitutions: list[UserConstitution], queries: list[str]):

        metrics = []
        for query, personalized_plan, normal_plan, constitution in tqdm.tqdm(list(zip(queries, personalized_plans, normal_plans, constitutions))):
            all_scores = dict()
            for strategy in personalized_plan.requirements.keys():
                if strategy not in normal_plan.requirements:
                    print('skipping!')
                    continue
                personalized_reqs, normal_reqs = personalized_plan.requirements[strategy], normal_plan.requirements[strategy]

                out_p = []
                for req in personalized_reqs:
                    inf_prompt = PLAN_CATEGORY_QUERY.format(query=query,
                                                        plan_step=req.text,
                                                        category=req.strategy_label.value,
                                                        definition=PERSONALIZATION_STRATEGY_RUBRIC[req.strategy_label] if req.strategy_label in PERSONALIZATION_STRATEGY_RUBRIC else PERSONALIZATION_FRAMEWORK_RUBRIC[req.strategy_label],
                                                        )
                    judgement_personalized = self.judge.generate_json(prompt=inf_prompt.strip(), target_json={'output': ''})
                    out_p.append(judgement_personalized['output'] == 'Match')

                out_n = []
                for req in normal_reqs:
                    inf_prompt = PLAN_CATEGORY_QUERY.format(query=query,
                                                    plan_step=req.text,
                                                    category=req.strategy_label.value,
                                                    definition=PERSONALIZATION_STRATEGY_RUBRIC[req.strategy_label] if req.strategy_label in PERSONALIZATION_STRATEGY_RUBRIC else PERSONALIZATION_FRAMEWORK_RUBRIC[req.strategy_label],
                                                    )
                    judgment_normal = self.judge.generate_json(prompt=inf_prompt.strip(), target_json={'output': ''})
                    out_n.append(judgment_normal['output'] == 'Match')


                all_scores[strategy] = ((out_p, out_n), str(personalized_plan), str(normal_plan))
            metrics.append(PlanMetrics(metrics=all_scores))

        return metrics
    
    def evaluate(self, personalized_plans: list[Plan], normal_plans: list[Plan], constitutions: list[UserConstitution], queries: list[str], query_ids: list[str], user_ids: list[str]):
        metrics_query = self.score_comparison_batch_query(personalized_plans=personalized_plans, normal_plans=normal_plans, constitutions=constitutions, queries=queries)
        print(metrics_query)
        metrics_personalized = self.score_comparison_batch_personalization(personalized_plans=personalized_plans, normal_plans=normal_plans, constitutions=constitutions, queries=queries)
        print(metrics_personalized)
        metrics_category = self.score_category_batch(personalized_plans=personalized_plans, normal_plans=normal_plans, constitutions=constitutions, queries=queries)
        print(metrics_category)

        keys = [(query_id, user_id) for query_id, user_id in zip(query_ids, user_ids)]
        return PlanEvalRun(metrics=dict(zip(keys, metrics_query))), PlanEvalRun(metrics=dict(zip(keys, metrics_personalized))), PlanEvalRun(metrics=dict(zip(keys, metrics_category)))