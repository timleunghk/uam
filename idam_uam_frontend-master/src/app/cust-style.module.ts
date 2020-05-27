import { NgModule } from '@angular/core';
import { ButtonModule } from 'primeng/button';
import { TableModule } from 'primeng/table';
import { InputTextModule } from 'primeng/inputtext';
import { CalendarModule } from 'primeng/calendar';
import { PanelModule } from 'primeng/panel';
import { ToastModule } from 'primeng/toast';
import { DialogModule } from 'primeng/dialog';
import { ConfirmDialogModule } from 'primeng/confirmdialog';
import { MessagesModule } from 'primeng/messages';
import { MessageModule } from 'primeng/message';
import { InputTextareaModule } from 'primeng/inputtextarea';
import { TabViewModule } from 'primeng/tabview';
import { CheckboxModule } from 'primeng/checkbox';
import { ProgressSpinnerModule } from 'primeng/progressspinner';
import { ScrollPanelModule } from 'primeng/scrollpanel';
import { FileUploadModule } from 'primeng/fileupload';
import { KeyFilterModule } from 'primeng/keyfilter';

@NgModule({
    declarations: [],
    imports: [ButtonModule, TableModule, InputTextModule, CalendarModule, PanelModule, ToastModule, DialogModule, ConfirmDialogModule, MessageModule, MessagesModule, InputTextareaModule,
        TabViewModule, CheckboxModule, ProgressSpinnerModule, ScrollPanelModule, FileUploadModule, KeyFilterModule],
    exports: [ButtonModule, TableModule, InputTextModule, CalendarModule, PanelModule, ToastModule, DialogModule, ConfirmDialogModule, MessageModule, MessagesModule, InputTextareaModule,
        TabViewModule, CheckboxModule, ProgressSpinnerModule, ScrollPanelModule, FileUploadModule, KeyFilterModule],
    providers: [],
})
export class CustStyleModule { }