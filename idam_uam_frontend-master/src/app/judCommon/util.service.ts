import { Injectable } from '@angular/core';
import { TitleCasePipe } from '@angular/common';
import { MessageService, SelectItem } from 'primeng/api';
import { HttpErrorResponse } from '@angular/common/http';
import { SimpleCode } from '../models/models';
import { FormGroup, AbstractControl } from '@angular/forms';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class UtilService {

  API_URL = environment.baseUrl;
  
  constructor(private titleCasePipe: TitleCasePipe, private messageService: MessageService) { }

  min(...x: number[]) {
    return Math.min(...x);
  }
  formatName(instr: string): string {
    if (instr) {
      return this.titleCasePipe.transform(instr.trim().replace(/\s{2,}/g, ' '))
    } else {
      return instr;
    }
  }

  private constructErrorDiv(errors: string[]): string {
    let tmp: string = "";
    errors.forEach(
      (element) => {
        tmp += `<div class='p-col-1'></div><div class='p-col-11'>${element}</div>`
      }
    )
    tmp = `<div class='p-grid'><div class='p-col-12'>The following error(s) occurred:</div>${tmp}</div>`;
    return tmp;
  }
  parseError(error: HttpErrorResponse) {
    console.log(error);
    if (error.status == 404) {
      return this.constructErrorDiv([`URL does not exist: ${error.url}`]);
    } else if (error.status == 400) {
      if ('error' in error) {
        let tmp: string[] = [];
        for (let key in error.error) {
          console.log(key);
          tmp.push(`${key}: ${error.error[key]}`);
        }
        return this.constructErrorDiv(tmp);
      }
    } else if (error.status == 403) {
      return this.constructErrorDiv(["You are not authorized to use this function"]);
    } else if (error.status == 401) {
      setTimeout(() => {
        window.location.href = `${this.API_URL}/auth/sso/`;
      }, 3000);
      return this.constructErrorDiv(['You are not logged in.  This page will be redirected to home page']);
    }
    return this.constructErrorDiv([error.message]);
  }

  promptError(error: HttpErrorResponse, heading: string) {
    this.messageService.add({ severity: 'error', summary: heading, detail: this.parseError(error), life: 2000, data: { icon: 'error' } });
  }

  convertSimpleCodeListToSelectItem(simpleCodes: SimpleCode[], formControl?: AbstractControl): SelectItem[] {
    let rtn: SelectItem[] = [];
    let defaultValue: any = null;
    for (let key in simpleCodes) {
      rtn.push({ 'label': simpleCodes[key]['name'], 'value': simpleCodes[key]['id'], 'is_default': simpleCodes[key].is_default } as SelectItem);
      if (simpleCodes[key].is_default && formControl) {
        if (formControl.value === null) {
          formControl.setValue(simpleCodes[key]['id']);
        }
      }
    }
    return rtn;
  }
  getDefaultValueFromSelectItem(items: SelectItem[]) {
    for (let i = 0; i < items.length; i++) {
      if (items[i]['is_default']) {
        return items[i].value;
      }
    }
    return null;
  }
  cloneFormToFlatObject(target: object, source: AbstractControl, controlName: string) {
    if (source instanceof FormGroup) {
      let tmp: FormGroup = source as FormGroup;
      Object.assign(target, tmp.getRawValue());
    } else {
      target[controlName] = source.value;
    }
  }
}
