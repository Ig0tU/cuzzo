import json
import os

def load_json(filepath):
    if not os.path.exists(filepath):
        print(f"Warning: {filepath} not found.")
        return {}
    with open(filepath, 'r') as f:
        return json.load(f)

def merge_matrix_databases(knowledge_db, resources_db):
    merged = knowledge_db.copy()

    # Merge resources_db
    for cluster_key, cluster_data in resources_db.items():
        if cluster_key in merged:
            # If cluster exists, merge nodes
            if "nodes" in cluster_data and isinstance(cluster_data["nodes"], dict):
                for node_key, node_data in cluster_data["nodes"].items():
                    # Check if node_data is a valid dictionary (not "...")
                    if isinstance(node_data, dict):
                        if "nodes" not in merged[cluster_key]:
                            merged[cluster_key]["nodes"] = {}
                        merged[cluster_key]["nodes"][node_key] = node_data
        else:
            # If cluster doesn't exist, add it (only if it has valid nodes)
             if "nodes" in cluster_data and isinstance(cluster_data["nodes"], dict):
                 valid_nodes = {k: v for k, v in cluster_data["nodes"].items() if isinstance(v, dict)}
                 if valid_nodes:
                     merged[cluster_key] = cluster_data
                     merged[cluster_key]["nodes"] = valid_nodes

    return merged

def generate_personas_markdown(matrix_db, sub_systems):
    content = "# PERSONAS_EXTENDED.md - Sovereign Orchestrator Roles\n\n"
    content += "Generated from `knowledge.json` and `resources.json`.\n\n"

    all_clusters = matrix_db.copy()

    # Flatten sub_systems into clusters for iteration if they have clusters
    if sub_systems:
        for sys_key, sys_data in sub_systems.items():
            if "clusters" in sys_data:
                for cluster_key, cluster_data in sys_data["clusters"].items():
                    # Add system info to cluster name for clarity
                    cluster_data["system_name"] = sys_data.get("name", sys_key)
                    all_clusters[cluster_key] = cluster_data

    # Sort clusters by priority if available, else by key
    sorted_clusters = sorted(all_clusters.items(), key=lambda x: (x[1].get("priority", 999), x[0]))

    for cluster_key, cluster_data in sorted_clusters:
        cluster_name = cluster_data.get("cluster", cluster_key)
        system_name = cluster_data.get("system_name", "")
        header = f"## {cluster_key}: {cluster_name}"
        if system_name:
            header += f" ({system_name})"
        content += f"{header}\n\n"

        if "description" in cluster_data:
             content += f"{cluster_data['description']}\n\n"

        if "health_check" in cluster_data:
             content += f"> Health Check: `{cluster_data['health_check']}`\n\n"

        if "nodes" in cluster_data and isinstance(cluster_data["nodes"], dict):
            # Sort nodes by key
            sorted_nodes = sorted(cluster_data["nodes"].items())
            for node_key, node_data in sorted_nodes:
                if not isinstance(node_data, dict):
                    continue

                name = node_data.get("name", "Unknown")
                keyword = node_data.get("keyword", "")
                persona = node_data.get("persona", "")

                content += f"### {node_key}: {name}\n"
                content += "```yaml\n"
                if keyword:
                    content += f"Activate: {keyword}\n"
                if persona:
                    content += f"Persona: \"{persona}\"\n"

                if "capabilities" in node_data:
                    content += f"Capabilities: {', '.join(node_data['capabilities'])}\n"

                if "enhancements" in node_data:
                    enh = node_data["enhancements"]
                    if "focus" in enh:
                        content += f"Focus: {', '.join(enh['focus'])}\n"
                    if "outputs" in enh:
                        content += f"Outputs: {', '.join(enh['outputs'])}\n"
                    if "quality_checks" in enh:
                        content += f"Quality_Checks: {', '.join(enh['quality_checks'])}\n"

                if "links" in node_data:
                     content += f"Resources: {len(node_data['links'])} datasets linked\n"

                content += "```\n\n"

        content += "---\n\n"

    return content

def generate_workflows_markdown(knowledge_logic, resources_logic):
    content = "# WORKFLOWS.md - Execution Logic\n\n"
    content += "Generated from `knowledge.json` and `resources.json`.\n\n"

    # Merge workflow rules
    workflow_rules = knowledge_logic.get("workflow_rules", []) + resources_logic.get("workflow_rules", [])

    content += "## Workflow Rules\n\n"

    for rule in workflow_rules:
        trigger = rule.get("trigger", "UNKNOWN_TRIGGER")
        description = rule.get("description", "")
        chain = rule.get("chain", [])

        content += f"### {trigger}\n"
        content += f"> {description}\n\n"
        content += f"**Chain:** `{' -> '.join(chain)}`\n\n"

        if "dynamic_variants" in rule:
            content += "**Dynamic Variants:**\n"
            for variant in rule["dynamic_variants"]:
                # The variant keys can vary (complexity, urgency, severity, etc.)
                # We'll just print key-value pairs that aren't 'chain'
                conditions = [f"{k}={v}" for k, v in variant.items() if k != "chain"]
                variant_chain = variant.get("chain", [])
                content += f"- **If {', '.join(conditions)}:** `{' -> '.join(variant_chain)}`\n"
            content += "\n"

        if "success_metrics" in rule:
            content += f"**Success Metrics:** {', '.join(rule['success_metrics'])}\n\n"

    content += "---\n\n"

    # Merge conditional logic
    conditional_logic = knowledge_logic.get("conditional_logic", {}).copy()
    conditional_logic.update(resources_logic.get("conditional_logic", {}))

    content += "## Conditional Logic\n\n"

    for condition_key, condition_data in conditional_logic.items():
        content += f"### {condition_key}\n"
        if "action" in condition_data:
            content += f"**Action:** {condition_data['action']}\n"

        if "nodes" in condition_data:
            content += f"**Trigger Nodes:** `{' + '.join(condition_data['nodes'])}`\n"

        if "additional" in condition_data:
            content += "**Additional Checks:**\n"
            for add in condition_data["additional"]:
                content += f"- {add}\n"

        content += "\n"

    return content

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    knowledge_path = os.path.join(base_dir, "knowledge.json")
    resources_path = os.path.join(base_dir, "resources.json")

    knowledge_data = load_json(knowledge_path)
    resources_data = load_json(resources_path)

    # Process Matrix Database (Personas)
    knowledge_matrix = knowledge_data.get("matrix_database", {})
    resources_matrix = resources_data.get("matrix_database", {})
    sub_systems = knowledge_data.get("sub_systems", {})

    merged_matrix = merge_matrix_databases(knowledge_matrix, resources_matrix)
    personas_content = generate_personas_markdown(merged_matrix, sub_systems)

    personas_path = os.path.join(base_dir, "PERSONAS_EXTENDED.md")
    with open(personas_path, 'w') as f:
        f.write(personas_content)
    print(f"Generated {personas_path}")

    # Process Workflow Logic
    knowledge_logic = knowledge_data.get("sequential_execution_logic", {})
    resources_logic = resources_data.get("sequential_execution_logic", {})

    workflows_content = generate_workflows_markdown(knowledge_logic, resources_logic)

    workflows_path = os.path.join(base_dir, "WORKFLOWS.md")
    with open(workflows_path, 'w') as f:
        f.write(workflows_content)
    print(f"Generated {workflows_path}")

if __name__ == "__main__":
    main()
