<template>
  <div v-if="singleSelectField === null" class="kanban-view__stacked-by-page">
    <KanbanViewStackedBy
      :table="table"
      :view="view"
      :fields="fields"
      :read-only="readOnly"
      :store-prefix="storePrefix"
      :include-field-options-on-refresh="true"
      @refresh="$emit('refresh', $event)"
    ></KanbanViewStackedBy>
  </div>
  <div
    v-else
    ref="kanban"
    v-auto-scroll="{
      orientation: 'horizontal',
      enabled: () => draggingRow !== null,
      speed: 6,
      padding: 12,
    }"
    class="kanban-view"
  >
    <div class="kanban-view__stacks">
      <KanbanViewStack
        :database="database"
        :table="table"
        :view="view"
        :card-fields="cardFields"
        :fields="fields"
        :read-only="readOnly"
        :store-prefix="storePrefix"
        @create-row="openCreateRowModal"
        @edit-row="openRowEditModal($event.id)"
        @refresh="$emit('refresh', $event)"
      ></KanbanViewStack>
      <KanbanViewStack
        v-for="option in existingSelectOption"
        :key="option.id"
        :option="option"
        :database="database"
        :table="table"
        :view="view"
        :card-fields="cardFields"
        :fields="fields"
        :read-only="readOnly"
        :store-prefix="storePrefix"
        @create-row="openCreateRowModal"
        @edit-row="openRowEditModal($event.id)"
        @refresh="$emit('refresh', $event)"
      ></KanbanViewStack>
      <a
        v-if="!readOnly"
        ref="addOptionContextLink"
        class="kanban-view__add-stack"
        @click="$refs.addOptionContext.toggle($refs.addOptionContextLink)"
      >
        <i class="fas fa-plus"></i>
      </a>
      <KanbanViewCreateStackContext
        ref="addOptionContext"
        :fields="fields"
        :store-prefix="storePrefix"
      ></KanbanViewCreateStackContext>
    </div>
    <RowCreateModal
      ref="rowCreateModal"
      :table="table"
      :primary-is-sortable="true"
      :visible-fields="cardFields"
      :hidden-fields="hiddenFields"
      :show-hidden-fields="showHiddenFieldsInRowModal"
      @toggle-hidden-fields-visibility="
        showHiddenFieldsInRowModal = !showHiddenFieldsInRowModal
      "
      @created="createRow"
      @order-fields="orderFields"
      @toggle-field-visibility="toggleFieldVisibility"
      @field-updated="$emit('refresh', $event)"
      @field-deleted="$emit('refresh')"
    ></RowCreateModal>
    <RowEditModal
      ref="rowEditModal"
      :database="database"
      :table="table"
      :primary-is-sortable="true"
      :visible-fields="cardFields"
      :hidden-fields="hiddenFields"
      :rows="allRows"
      :read-only="false"
      :show-hidden-fields="showHiddenFieldsInRowModal"
      @hidden="$emit('selected-row', undefined)"
      @toggle-hidden-fields-visibility="
        showHiddenFieldsInRowModal = !showHiddenFieldsInRowModal
      "
      @update="updateValue"
      @order-fields="orderFields"
      @toggle-field-visibility="toggleFieldVisibility"
      @field-updated="$emit('refresh', $event)"
      @field-deleted="$emit('refresh')"
      @field-created="
        fieldCreated($event)
        showHiddenFieldsInRowModal = true
      "
    ></RowEditModal>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import { clone } from '@baserow/modules/core/utils/object'
import { populateRow } from '@baserow/modules/database/store/view/grid'
import { notifyIf } from '@baserow/modules/core/utils/error'
import viewHelpers from '@baserow/modules/database/mixins/viewHelpers'
import {
  sortFieldsByOrderAndIdFunction,
  filterVisibleFieldsFunction,
  filterHiddenFieldsFunction,
} from '@baserow/modules/database/utils/view'
import RowCreateModal from '@baserow/modules/database/components/row/RowCreateModal'
import RowEditModal from '@baserow/modules/database/components/row/RowEditModal'
import kanbanViewHelper from '@baserow_premium/mixins/kanbanViewHelper'
import KanbanViewStack from '@baserow_premium/components/views/kanban/KanbanViewStack'
import KanbanViewStackedBy from '@baserow_premium/components/views/kanban/KanbanViewStackedBy'
import KanbanViewCreateStackContext from '@baserow_premium/components/views/kanban/KanbanViewCreateStackContext'

export default {
  name: 'KanbanView',
  components: {
    RowCreateModal,
    RowEditModal,
    KanbanViewCreateStackContext,
    KanbanViewStackedBy,
    KanbanViewStack,
  },
  mixins: [viewHelpers, kanbanViewHelper],
  props: {
    database: {
      type: Object,
      required: true,
    },
    table: {
      type: Object,
      required: true,
    },
    view: {
      type: Object,
      required: true,
    },
    fields: {
      type: Array,
      required: true,
    },
    readOnly: {
      type: Boolean,
      required: true,
    },
    row: {
      validator: (prop) => typeof prop === 'object' || prop === null,
      required: true,
    },
  },
  data() {
    return {
      showHiddenFieldsInRowModal: false,
    }
  },
  computed: {
    /**
     * Returns the visible field objects in the right order.
     */
    cardFields() {
      const fieldOptions = this.fieldOptions
      return this.fields
        .filter(filterVisibleFieldsFunction(fieldOptions))
        .sort(sortFieldsByOrderAndIdFunction(fieldOptions))
    },
    hiddenFields() {
      const fieldOptions = this.fieldOptions
      return this.fields
        .filter(filterHiddenFieldsFunction(fieldOptions))
        .sort(sortFieldsByOrderAndIdFunction(fieldOptions))
    },
    /**
     * Returns the single select field object that the kanban view uses to group the
     * cards in stacks.
     */
    singleSelectField() {
      const allFields = this.fields
      for (let i = 0; i < allFields.length; i++) {
        if (allFields[i].id === this.singleSelectFieldId) {
          return allFields[i]
        }
      }
      return null
    },
    existingSelectOption() {
      return this.singleSelectField.select_options.filter((option) => {
        return this.$store.getters[
          this.$options.propsData.storePrefix + 'view/kanban/stackExists'
        ](option.id)
      })
    },
  },
  beforeCreate() {
    this.$options.computed = {
      ...(this.$options.computed || {}),
      ...mapGetters({
        singleSelectFieldId:
          this.$options.propsData.storePrefix +
          'view/kanban/getSingleSelectFieldId',
        allRows: this.$options.propsData.storePrefix + 'view/kanban/getAllRows',
        draggingRow:
          this.$options.propsData.storePrefix + 'view/kanban/getDraggingRow',
      }),
    }
  },
  mounted() {
    if (this.row !== null) {
      const rowClone = populateRow(clone(this.row))
      this.$refs.rowEditModal.show(this.row.id, rowClone)
    }
  },
  methods: {
    /**
     * When the row edit modal is opened we notifiy
     * the Table component that a new row has been selected,
     * such that we can update the path to include the row id.
     */
    openRowEditModal(rowId) {
      this.$refs.rowEditModal.show(rowId)
      this.$emit('selected-row', rowId)
    },
    openCreateRowModal(event) {
      const defaults = {}
      if (event.option !== null) {
        const name = `field_${this.singleSelectField.id}`
        defaults[name] = clone(event.option)
      }
      this.$refs.rowCreateModal.show(defaults)
    },
    async createRow({ row, callback }) {
      try {
        await this.$store.dispatch(
          this.storePrefix + 'view/kanban/createNewRow',
          {
            view: this.view,
            table: this.table,
            fields: this.fields,
            values: row,
          }
        )
        callback()
      } catch (error) {
        callback(error)
      }
    },
    async updateValue({ field, row, value, oldValue }) {
      try {
        await this.$store.dispatch(
          this.storePrefix + 'view/kanban/updateRowValue',
          {
            table: this.table,
            view: this.view,
            fields: this.fields,
            row,
            field,
            value,
            oldValue,
          }
        )
      } catch (error) {
        notifyIf(error, 'field')
      }
    },
  },
}
</script>
