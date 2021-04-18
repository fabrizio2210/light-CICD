<template>
    <div>
        <form @submit.prevent="handleSubmitNew">
            <div class="form-group">
                <label for="newenvname">Env Name</label>
                <input type="text" v-model="newenvname" name="newenvname" class="form-control" :class="{ 'is-invalid': submitted && !newenvname }" />
                <div v-show="submitted && !newenvname" class="invalid-feedback">Env Name is required</div>
            </div>
            <div class="form-group">
                <button class="btn btn-primary" :disabled="creating" >New Env</button>
                <img v-show="creating" src="../assets/loading.gif" />
            </div>
        </form>
        <em v-if="environments.loading">Loading environment...</em>
        <img v-show="environments.loading" src="../assets/loading.gif" />
        <span v-if="environments.error" class="text-danger">ERROR: {{environments.error}}</span>
        <ul v-if="environments.environments">
            <li>
                <span>Name</span>
                <span>Value</span>
                <span>Description</span>
            </li>
            <li v-for="env in environments.environments" :key="env.id">
                <form @submit.prevent="handleSubmit(env.id)">
                    <div class="form-group">
                        <label for="envname">{{ env.id + ': '}}</label>
                        <input type="text" v-on:keydown="env.untouched=false" v-model="env.name" name="envname" class="form-control" />
                        <textarea v-on:keydown="env.untouched=false" v-model="env.value" name="envvalue" class="form-control" rows="1" />
                        <input type="text" v-on:keydown="env.untouched=false" v-model="env.description" name="envdescription" class="form-control" />
                        <button class="btn btn-primary" :disabled="env.untouched||updating" >Update</button>
                    </div>
                </form>
            </li>
        </ul>
    </div>
</template>

<script>
export default {
    data () {
        return {
            newenvname: '',
            submitted: false
        }
    },
    computed: {
        creating () {
            return this.$store.state.projectenvironments.status.creating;
        },
        updating () {
            return this.$store.state.projectenvironments.status.updating;
        },
        environments () {
            const project_id = this.$route.params.project_id;
            return this.$store.state.projectenvironments.all.environments_dicts[project_id];
        }
    },
    methods: {
        handleSubmitNew () {
            this.submitted = true;
            const project_id = this.$route.params.project_id;
            const { newenvname } = this;
            const { dispatch } = this.$store;
            if (newenvname) {
                dispatch('projectenvironments/creating', { project_id, newenvname });
            }
        },
        handleSubmit (envid) {
            console.log(envid);
            console.log(this.environments);
            const project_id = this.$route.params.project_id;
            const envvalue = this.environments.environments[envid].value;
            const envname = this.environments.environments[envid].name;
            const envdescription = this.environments.environments[envid].description;
            const { dispatch } = this.$store;
            if (envname) {
                dispatch('projectenvironments/updating', { project_id, envid, envname, envvalue, envdescription });
            }
        }
    },
    created () {
        const project_id = this.$route.params.project_id;
        this.$store.dispatch('projectenvironments/getAll', { project_id });
    }
};
</script>
