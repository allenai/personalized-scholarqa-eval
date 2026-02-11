import datasets
from datasets.utils.logging import disable_progress_bar
disable_progress_bar()

DEFAULT_SPLIT = None

from data import UserConstitution, Plan
class DatasetLoader:

    def __init__(self, ds_name):
        self.ds = datasets.load_from_disk(ds_name)

    def __init__(self, ds_name: str | None = None):
        self.ds = {}
        if ds_name is not None:
            self.ds = datasets.load_from_disk(ds_name)
    
    @classmethod
    def from_subsets(cls, ds_name, subsets):
        obj = cls.__new__(cls)
        obj.ds = {
            subset: datasets.load_from_disk(f"{ds_name}/{subset}")
            for subset in subsets
        }
        return obj

    """
    Returns a map of author ID to similarity types:
        1. map of author_id (str) to author_type ('low' | 'medium' | 'high')
    """
    def load_author_map(self) -> dict[str, str]:
        author_map = dict()
        for k in self.ds.keys():
            curr_ds = self.ds[k]
            for row_idx in range(curr_ds.num_rows):
                row = curr_ds[row_idx]
                for name in ['high', 'low', 'medium']:
                    if row[f'{name}_similarity_author_papers'] and row[f'{name}_similarity_author_id']:
                        author_map[row[f'{name}_similarity_author_id']] = name
        return author_map
                        

    """
    Returns data needed to generate profiles:
        1. list of paper_id collections
        2. list of author_ids
    """
    def load_constitution_inputs(self, num_examples: int) -> tuple[list[list[str]], list[str]]:

        paper_collection_ids = []
        author_ids = []
        for k in self.ds.keys():
            curr_ds = self.ds[k]
            num_ds_examples = len(curr_ds) if num_examples == 0 else num_examples
            for row_idx in range(num_ds_examples):
                row = curr_ds[row_idx]
                for name in ['high', 'low', 'medium']:
                    if row[f'{name}_similarity_author_papers'] and row[f'{name}_similarity_author_id']:
                        paper_collection_ids.append(row[f'{name}_similarity_author_papers'])
                        author_ids.append(row[f'{name}_similarity_author_id'])

        assert len(paper_collection_ids) == len(author_ids)
        return paper_collection_ids, author_ids
    
    """
    Returns data for evaluating profiles:
        1. list of constitutions
        2. list of author_ids
    """
    def load_constitution_outputs(self, output_dir: str, num_examples: int, split: str | None = DEFAULT_SPLIT) -> tuple[list[UserConstitution], list[str]]:
        constitutions = []
        author_ids = []
        num_skipped = 0
        for k in self.ds.keys():
            if split != None and split != k:
                continue
            curr_ds = self.ds[k]
            num_examples_ds = len(curr_ds) if num_examples == 0 else num_examples
            for row_idx in range(num_examples_ds):
                row = curr_ds[row_idx]
                for name in ['high', 'low', 'medium']:
                    if row[f'{name}_similarity_author_papers'] and row[f'{name}_similarity_author_id']:
                        try:
                            constitution = UserConstitution.from_json(output_dir, row[f'{name}_similarity_author_id'])
                            constitutions.append(constitution)
                            author_ids.append(row[f'{name}_similarity_author_id'])
                        except Exception as e:
                            print(e)
                            num_skipped += 1
                            pass
        print('Num Constitutions:', len(constitutions))
        if num_skipped:
            print(f"     - Warning: Skipped {num_skipped} due to parsing issues")
        assert len(constitutions) == len(author_ids)
        return constitutions, author_ids

    """
    Returns data for evaluating individual plans:
        1. list of queries
        2. list of query ids for (1)
        3. list of constitutions
        4. list of user ids for (3)
    """
    def load_plan_inputs(self, profile_dir: str, num_examples: int) -> tuple[list[str], list[str], list[UserConstitution], list[str]]:
        constitutions = []
        user_ids = []
        queries = []
        query_ids = []
        for k in self.ds.keys():
            curr_ds = self.ds[k]
            num_ds_examples = len(curr_ds) if num_examples == 0 else num_examples
            for row_idx in range(num_ds_examples):
                row = curr_ds[row_idx]
                for name in ['high', 'low', 'medium']:
                    if row[f'{name}_similarity_author_papers'] and row[f'{name}_similarity_author_id']:
                        queries.append(row['query'])
                        query_ids.append(row['query_id'])
                        user_ids.append(row[f'{name}_similarity_author_id'])
                        constitution = UserConstitution.from_json(output_dir=profile_dir, user_id=row[f'{name}_similarity_author_id'])
                        constitutions.append(constitution)
                
        assert len(queries) == len(constitutions)
        assert len(queries) == len(query_ids)
        return queries, query_ids, constitutions, user_ids

    """
    Returns data for comparing personalized and generic plans on the same queries:
        1. list of queries
        2. list of query ids for (1)
        3. list of personalized plans for each query
        4. list of generic plans for each query
        5. list of user ids for (4)
    """
    def load_plan_pairs(self, constitution_dir: str, plan_dir: str, num_examples: int, split: str | None = DEFAULT_SPLIT) -> tuple[dict, dict]:
        dataset_dict = {'constitution': [], 'normal_plan': [], 'personalized_plan': [], 'query': [], 'user_id': [], 'query_id': []}
        for k in self.ds.keys():
            if split != None and split != k:
                continue
            curr_ds = self.ds[k]
            for row_idx in range(num_examples):
                row = curr_ds[row_idx]
                for author_name in ['high', 'low', 'medium']:
                    if row[f'{author_name}_similarity_author_papers'] and row[f'{author_name}_similarity_author_id']:
                        normal_plan = Plan.from_json(output_dir=plan_dir, query_id=row['query_id'] + '_normal', user_id=row[f'{author_name}_similarity_author_id'])
                        personalized_plan = Plan.from_json(output_dir=plan_dir, query_id=row['query_id'] + '_personalized', user_id=row[f'{author_name}_similarity_author_id'])
                        constitution = UserConstitution.from_json(output_dir=constitution_dir, user_id=row[f'{author_name}_similarity_author_id'])
                        dataset_dict['constitution'].append(constitution)
                        dataset_dict['normal_plan'].append(normal_plan)
                        dataset_dict['personalized_plan'].append(personalized_plan)
                        dataset_dict['query'].append(row['query'])
                        dataset_dict['query_id'].append(row['query_id'])
                        dataset_dict['user_id'].append(row[f'{author_name}_similarity_author_id'])
        return dataset_dict

    def load_simulation_data(self):

        all_data = self.ds['all_text']['train']
        def retrieve_text(task_id: str):
            return all_data.filter(lambda ex: ex['source_ids'][0] == task_id)['generation'][0]

        final_ds = {}
        for split in ['profile', 'plan', 'response']:
            curr_ds = self.ds[split]['val']
            source_texts = []
            for source_id_list in curr_ds['source_ids']:
                sources = []
                for source_id in source_id_list:
                    sources.append(retrieve_text(source_id))
                source_texts.append(sources)
            curr_ds = curr_ds.add_column('source_texts', source_texts)
            final_ds[split] = curr_ds
        
        final_ds = datasets.DatasetDict(final_ds)
        return final_ds