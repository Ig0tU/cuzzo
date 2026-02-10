import json
import os

def load_json(filepath):
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return {}
    with open(filepath, 'r') as f:
        return json.load(f)

def generate_personas(knowledge, resources):
    markdown_lines = []
    markdown_lines.append("# PERSONAS_EXTENDED.md - Advanced Behavioral Profiles")
    markdown_lines.append("")
    markdown_lines.append("> Extended from SOVEREIGN_ORCHESTRATOR_v3")
    markdown_lines.append("")

    # Process Knowledge clusters
    if 'matrix_database' in knowledge:
        for cluster_key, cluster_data in knowledge['matrix_database'].items():
            cluster_name = cluster_data.get('cluster', 'Unknown Cluster')
            markdown_lines.append(f"## {cluster_key}: {cluster_name}")
            markdown_lines.append("")

            nodes = cluster_data.get('nodes', {})
            for node_key, node_data in nodes.items():
                if isinstance(node_data, str): # Skip "..." placeholders
                    continue

                name = node_data.get('name', node_key)
                persona_desc = node_data.get('persona', '')
                keyword = node_data.get('keyword', '').replace('/', '')

                enhancements = node_data.get('enhancements', {})
                focus = ', '.join(enhancements.get('focus', []))
                outputs = ', '.join(enhancements.get('outputs', []))
                quality_checks = ', '.join(enhancements.get('quality_checks', []))
                capabilities = ', '.join(node_data.get('capabilities', []))

                # Format similar to PERSONAS.md
                markdown_lines.append(f"### {keyword} ({name})")
                markdown_lines.append("```yaml")
                markdown_lines.append(f"Core_Belief: {persona_desc}")
                markdown_lines.append(f"Focus: {focus} | Outputs: {outputs}")
                markdown_lines.append(f"Quality_Checks: {quality_checks}")
                markdown_lines.append(f"Capabilities: {capabilities}")
                markdown_lines.append("```")
                markdown_lines.append("")

    # Process Resources clusters (Cluster H)
    if 'matrix_database' in resources:
        for cluster_key, cluster_data in resources['matrix_database'].items():
            # Check if it's a full definition (dict with 'nodes')
            if not isinstance(cluster_data, dict) or 'nodes' not in cluster_data:
                continue

            cluster_name = cluster_data.get('cluster', 'Unknown Cluster')
            markdown_lines.append(f"## {cluster_key}: {cluster_name}")
            markdown_lines.append("")

            nodes = cluster_data.get('nodes', {})
            for node_key, node_data in nodes.items():
                if isinstance(node_data, str):
                    continue

                name = node_data.get('name', node_key)
                persona_desc = node_data.get('persona', '')
                keyword = node_data.get('keyword', '').replace('/', '')
                links = ', '.join(node_data.get('links', []))

                markdown_lines.append(f"### {keyword} ({name})")
                markdown_lines.append("```yaml")
                markdown_lines.append(f"Core_Belief: {persona_desc}")
                markdown_lines.append(f"Links: {links}")
                markdown_lines.append("```")
                markdown_lines.append("")

    # Process Sub-systems in Knowledge
    if 'sub_systems' in knowledge:
        for sys_key, sys_data in knowledge['sub_systems'].items():
            sys_name = sys_data.get('name', sys_key)
            markdown_lines.append(f"## {sys_key}: {sys_name}")
            markdown_lines.append("")

            if 'clusters' in sys_data:
                for cluster_key, cluster_data in sys_data['clusters'].items():
                    cluster_name = cluster_data.get('cluster', 'Unknown Sub-Cluster')
                    markdown_lines.append(f"### {cluster_key}: {cluster_name}")
                    markdown_lines.append("")

                    nodes = cluster_data.get('nodes', {})
                    for node_key, node_data in nodes.items():
                        name = node_data.get('name', node_key)
                        keyword = node_data.get('keyword', '').replace('/', '')
                        capabilities = ', '.join(node_data.get('capabilities', []))

                        enhancements = node_data.get('enhancements', {})
                        focus = ', '.join(enhancements.get('focus', []))
                        outputs = ', '.join(enhancements.get('outputs', []))

                        markdown_lines.append(f"#### {keyword} ({name})")
                        markdown_lines.append("```yaml")
                        markdown_lines.append(f"Focus: {focus}")
                        markdown_lines.append(f"Outputs: {outputs}")
                        markdown_lines.append(f"Capabilities: {capabilities}")
                        markdown_lines.append("```")
                        markdown_lines.append("")


    return "\n".join(markdown_lines)

def generate_workflows(knowledge, resources):
    markdown_lines = []
    markdown_lines.append("# WORKFLOWS.md - Execution Logic")
    markdown_lines.append("")

    datas = [knowledge, resources]

    for data in datas:
        if 'sequential_execution_logic' in data:
            logic = data['sequential_execution_logic']

            if 'workflow_rules' in logic:
                markdown_lines.append("## Workflow Rules")
                markdown_lines.append("")
                for rule in logic['workflow_rules']:
                    trigger = rule.get('trigger', 'UNKNOWN')
                    description = rule.get('description', '')
                    chain = " -> ".join(rule.get('chain', []))

                    markdown_lines.append(f"### Trigger: {trigger}")
                    markdown_lines.append("```yaml")
                    markdown_lines.append(f"Description: {description}")
                    markdown_lines.append(f"Default Chain: {chain}")

                    if 'dynamic_variants' in rule:
                        variants = []
                        for v in rule['dynamic_variants']:
                            # Find the key that is not 'chain'
                            condition = [k for k in v.keys() if k != 'chain'][0]
                            val = v[condition]
                            v_chain = " -> ".join(v.get('chain', []))
                            variants.append(f"{condition}={val} => {v_chain}")

                        markdown_lines.append(f"Variants: {'; '.join(variants)}")

                    if 'success_metrics' in rule:
                        markdown_lines.append(f"Metrics: {', '.join(rule['success_metrics'])}")

                    markdown_lines.append("```")
                    markdown_lines.append("")

            if 'conditional_logic' in logic:
                markdown_lines.append("## Conditional Logic")
                markdown_lines.append("")
                for condition_key, condition_data in logic['conditional_logic'].items():
                    action = condition_data.get('action', '')
                    nodes = ", ".join(condition_data.get('nodes', []))

                    markdown_lines.append(f"### {condition_key}")
                    markdown_lines.append("```yaml")
                    markdown_lines.append(f"Action: {action}")
                    markdown_lines.append(f"Trigger Nodes: {nodes}")
                    if 'additional' in condition_data:
                        markdown_lines.append(f"Additional: {', '.join(condition_data['additional'])}")
                    markdown_lines.append("```")
                    markdown_lines.append("")

    return "\n".join(markdown_lines)

def main():
    base_dir = "SuperClaude"
    knowledge_path = os.path.join(base_dir, "knowledge.json")
    resources_path = os.path.join(base_dir, "resources.json")

    knowledge = load_json(knowledge_path)
    resources = load_json(resources_path)

    personas_md = generate_personas(knowledge, resources)
    with open(os.path.join(base_dir, "PERSONAS_EXTENDED.md"), 'w') as f:
        f.write(personas_md)

    workflows_md = generate_workflows(knowledge, resources)
    with open(os.path.join(base_dir, "WORKFLOWS.md"), 'w') as f:
        f.write(workflows_md)

    print("Files generated successfully.")

if __name__ == "__main__":
    main()
