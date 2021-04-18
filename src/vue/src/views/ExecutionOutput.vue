<template>
    <div>
        <div class="executionoutput-group">
            <button v-on:click="handleSubmit" class="btn btn-primary" :disabled="fetching" >Fetch</button>
            <img v-show="fetching" src="../assets/loading.gif" />
        </div>
        <em v-if="output.loading">Loading output...</em>
        <img v-show="output.loading" src="../assets/loading.gif" />
        <span v-if="output.error" class="text-danger">ERROR: {{output.error}}</span>
        <div class="output" v-if="output.output">
            {{ output.output.data }}
        </div>
    </div>
</template>

<script>
export default {
    data () {
        return {
        }
    },
    computed: {
        fetching () {
            return this.$store.state.executionoutputs.status.fetching;
        },
        output () {
            const project_id = this.$route.params.project_id;
            const execution_id = this.$route.params.exec_id;
            if (this.$store.state.executionoutputs.all.output_dicts[project_id]) {
                if (this.$store.state.executionoutputs.all.output_dicts[project_id][execution_id]) {
                    return this.$store.state.executionoutputs.all.output_dicts[project_id][execution_id];
                } else {
                    return {};
                }
            } else {
                return {};
            }
        }
    },
    methods: {
        handleSubmit () {
            this.submitted = true;
            const { dispatch } = this.$store;
            const project_id = this.$route.params.project_id;
            const execution_id = this.$route.params.exec_id;
            const f_byte = 0;
            const l_byte = -1;
            dispatch('executionoutputs/fetching', { project_id, execution_id, f_byte, l_byte });
        }
    },
    created () {
        const project_id = this.$route.params.project_id;
        const execution_id = this.$route.params.exec_id;
        const f_byte = 0;
        const l_byte = 0;
        this.$store.dispatch('executionoutputs/fetching', { project_id, execution_id, f_byte, l_byte });
    }
};
</script>
